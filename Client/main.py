import json
import os
import random
import sys
import time
import uuid
import socket
import webbrowser
from concurrent.futures import ThreadPoolExecutor
import librosa
import numpy as np
import pyotp
import qrcode
import rsa
from jnius import autoclass, cast
from PIL import Image
from kivy.metrics import dp
from plyer import notification

root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(root_dir, "libs", "applibs"))
sys.path.insert(0, os.path.join(root_dir, "libs", "uix"))

from kivy.app import App
import kivy
from kivy.core.window import Window
from kivy.utils import platform, get_color_from_hex
from datetime import datetime
from kivy.uix.image import Image as Image_Kivy
from components.chat_bubble import ImageMessage
from components.chat_bubble import Attachment
from components.chat_bubble import AudioMessage
from components.chat_bubble import ChatBubble2

import components
from androspecific import statusbar
from core.theming import ThemeManager
from root import Root
from utils.configparser import config
from components.toast import toast
import shutil
import concurrent.futures


from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, OptionProperty
from kivy.clock import Clock, mainthread

from functools import partial
from plyer import filechooser

from security import *
import threading

from deep_translator import GoogleTranslator
from core.encryption import encrypt, decrypt
from dmk_support import *

import requests


# class requests:
#     @staticmethod
#     def get(url, json=None, headers=None, data=None, params=None):
#         return grequests.map([grequests.get(url, json=json)])[0]
#
#     @staticmethod
#     def post(url, json=None, headers=None, data=None, params=None):
#         return grequests.map([grequests.post(url, json=json)])[0]


if platform != "android":
    Window.size = (350, 650)
else:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from android.runnable import run_on_ui_thread
    from android import mActivity as mA

conn = "socket.protdos.com", 5002


def create_loudness_intervals(audio_file, num_intervals=38, num_threads=4):
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Calculate the interval length
    interval_length = len(y) // num_intervals

    def process_intervals(start_idx):
        end_idx = start_idx + interval_length
        audio_segment = y[start_idx:end_idx]
        loudness = np.sqrt(np.mean(audio_segment ** 2))  # Faster RMS calculation
        return loudness

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        start_indices = range(0, len(y), interval_length)
        loudness_list = list(executor.map(process_intervals, start_indices))

    f = 20 / max(loudness_list)
    return [round(item * f, 2) for item in loudness_list]


def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff']
    _, extension = os.path.splitext(file_path)
    return extension.lower() in image_extensions


def is_audio_file(file_path):
    audio_extensions = [".wav", ".mp3"]
    _, extension = os.path.splitext(file_path)
    return extension.lower() in audio_extensions


def extract_links(text):
    # Regular expression to match URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'

    suffix = "[/color][/ref]"

    # Find all URLs in the text
    links = re.findall(url_pattern, text)
    modified_text = text
    for link in links:
        modified_link = f"[ref={link}][color=#0000EE]" + link + suffix
        modified_text = modified_text.replace(link, modified_link)

    return modified_text


def delete_dict_by_uid(lst, uid):
    print(lst)
    for item in lst:
        print(item)
        if item.get("idd") == uid:
            lst.remove(item)
            return True  # Return True if a match is found and deleted
    return False  # Return False if no match is found


def get_dict_by_uid(lst, uid):
    print(lst)
    for item in lst:
        print(item)
        if item.get("idd") == uid:
            item["icon"] = "check_circle"
            return lst
    return lst


def convert_bytes(size, unit="B"):
    # List of possible units for conversion
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    # Loop to find the appropriate unit for the file size
    while size >= 1024 and units:
        size /= 1024.0
        unit = units.pop(0)

    return f"{size:.1f} {unit}"


def get_file_size(file_path):
    if os.path.isfile(file_path):
        size = os.path.getsize(file_path)
        return convert_bytes(size)
    else:
        return "File not found"



def resize_image(original_width, original_height, target_width, target_height):
    aspect_ratio = original_width / original_height

    # Calculate the new dimensions while preserving aspect ratio
    if aspect_ratio > 1:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    return [new_width, new_height]


# TRANSLATION BEGINNING
def load_translations(file_path="assets/translations.json"):
    with open(file_path, 'r') as file:
        return json.load(file)


def save_translations(translations, file_path="assets/translations.json"):
    with open(file_path, 'w') as file:
        json.dump(translations, file, indent=4)


def add_new_translation(word, country_code, translation, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                print(f"Translation for '{word}' already exists for country code '{country_code}'.")
                return

        translations[word].append({country_code: translation})
    else:
        translations[word] = [{country_code: translation}]

    save_translations(translations, file_path)


def add_translation_to_existing(word, country_code, translation, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                print(f"Translation for '{word}' already exists for country code '{country_code}'.")
                return

        existing_translations.append({country_code: translation})
        save_translations(translations, file_path)
    else:
        print(f"Translation for '{word}' does not exist in the translations file.")


def get_translation(word, country_code, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                return entry[country_code]
        return "_not for country code_"
    else:
        return "_not in translation_"

# TRANSLATION ENDING


def rename_variable_in_dict(dictionary, old_variable_name, new_variable_name):
    if old_variable_name in dictionary:
        value = dictionary[old_variable_name]
        del dictionary[old_variable_name]
        dictionary[new_variable_name] = value
    return dictionary


def change_avatar():
    print("Not available")


def is_device_rooted():
    # Common paths where binaries related to root access are stored
    root_binaries = [
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/system/app/Superuser.apk",
        "/system/app/SuperSU.apk",
    ]

    # Check if any of the common root binaries exist
    for binary_path in root_binaries:
        if os.path.exists(binary_path):
            return True

    return False


def delete_metadata(image_path):
    image = Image.open(image_path)

    # next 3 lines strip exif
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    return image_without_exif.tobytes()


def split_and_process(data, pub):
    block_size = 50
    num_blocks = (len(data) + block_size - 1) // block_size  # Calculate the number of blocks

    blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]  # Split the data into blocks

    processed_blocks = []
    for block in blocks:
        processed_blocks.append(rsa.encrypt(block, pub))

    return processed_blocks


def combine_blocks(blocks, priv):
    dec = []
    for block in blocks:
        a = rsa.decrypt(block, priv)
        dec.append(a)
    opt = b"".join(dec)
    return opt


def delete_all():
    a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), "w")
    a.write("{}")
    a.close()

    return True


class PurpApp(App):
    theme_cls = ThemeManager()
    trans = ObjectProperty()
    settings = ObjectProperty()
    refreshing = BooleanProperty(False)

    language = OptionProperty(config.get_language().upper(), options=('EN', 'DE', "ES", "FR", "ZH", "AR", "BN", "RU", "PT", "UR", "ID", "JA", "SW", "PA"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._stop_event = threading.Event()
        self.message_thread = threading.Thread()

        self.title = "Veilo"
        self.icon = "assets/images/logo.png"

        self.theme_cls.theme_style = config.get_theme_style()

        Window.keyboard_anim_args = {"d": 0.2, "t": "in_out_expo"}  # linear
        Window.softinput_mode = "below_target"

        self.long_press_duration = 0.3  # Adjust this value to change the long press duration
        self.is_touching = False
        self.long_press_trigger = None

        self.id = None
        self.has_2fa = None
        self.username = StringProperty("")
        self.username_test = StringProperty("Stay")
        self.password = None
        self.unhashed_password = None
        self.public_key = None
        self.private_key = None
        self.current_chat_with = None

        self.socket_connection = None

        """
        In this socket connection, no identifiable data is transmitted (e.g. username, hashed_password, public_key),
        so that the connection remains anonymous. This connection is used for the sealed sender concept,
        where the server is not allowed to have that kind of information
        """
        self.anonymous_socket_connection = None

        self.current_socket = None

        self.public_key_of_partner = None

        self.last_sent = True

        self.avatar_path = "default.jpg" if not os.path.exists(f"user_avatars/{self.id}") else f"user_avatars/{self.id}"

        self.tries_left = 4

        self.session = requests.Session()

    def build(self):
        try:
            if platform == 'android':
                # Get the current Android activity
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = cast('android.content.Context', PythonActivity.mActivity)

                java_class_name = 'android.widget.EditText'

                # Load the class using pyjnius
                EditText = autoclass(java_class_name)

                # Now, you can use the EditText class in your Kivy code
                # For example, you can use it to create a new instance of EditText:
                my_edit_text = EditText(context)

                # Set the IME options flag using the correct integer value
                my_edit_text.setImeOptions(16777216)
        except:
            print("Private keyboard didn't work.")

        self.icon = r"assets/images/logo.png"
        self.root = Root()
        c = config.is_startup()
        print("asasd", c)
        if c != "False":
            self.root.set_current("startup")
        else:
            self.root.set_current("auth")  # auth

    def stop_thread(self):
        self._stop_event.set()

    try:
        def on_start(self):
            statusbar.set_color(self.theme_cls.primary_color)

            if platform == "android":
                LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                window = mA.getWindow()
                params = window.getAttributes()
                params.setDecorFitsSystemWindows = False
                params.layoutInDisplayCutoutMode = LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                window.setAttributes(params)
                window.setFlags(LayoutParams.FLAG_SECURE, LayoutParams.FLAG_SECURE)
                window.addFlags(LayoutParams.FLAG_SECURE)
    except:
        print("First didn't work.")
        try:
            @run_on_ui_thread
            def on_start(self):
                statusbar.set_color(self.theme_cls.primary_color)

                if platform == "android":
                    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                    window = mA.getWindow()
                    params = window.getAttributes()
                    params.setDecorFitsSystemWindows = False
                    params.layoutInDisplayCutoutMode = LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                    window.setAttributes(params)
                    window.setFlags(LayoutParams.FLAG_SECURE, LayoutParams.FLAG_SECURE)
                    window.addFlags(LayoutParams.FLAG_SECURE)
        except:
            print("Second didn't work.")

    def destroy_pop(self, dt):
        self.root.get_screen("home").popup.dismiss(force=True)
    
    @mainthread
    def toast(self, message):
        toast(message)

    def create_chat(self, rec):
        self.root.get_screen("home").popup.dismiss(force=True)

        Clock.schedule_once(partial(self.create_chat_2, rec), 0)

    def create_chat_2(self, rec, *args):
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')),
                  'r') as file:
            data = json.load(file)
        print(data)
        print(rec)
        print(self.unhashed_password)

        if rec == "":
            self.toast("Please enter a recipient")
            return

        for item in data:
            if decrypt(item, self.unhashed_password) == rec:
                # self.toast("Already added.")
                # self.current_chat_with = rec
                # self.start_chat()
                self.root.get_screen("home").goto_chat_screen(rec)
                return
        r = self.session.post("http://api.protdos.com/user/id", json={"recipient": rec}).json()
        print(r)
        if r["code"] != 11110:
            self.toast("Invalid recipient.")
            return
        idd = r["id"]

        r = self.session.post("http://api.protdos.com/user/avatar", json={"id": idd})

        file_name = f'user_avatars/{idd}.png'

        with open(file_name, "wb") as f:
            f.write(r.content)

        with open('assets/users.json', 'r') as file:
            data = json.load(file)

        t = str(f"{datetime.now().strftime('%H:%M')}")

        message = "test"
        about = "test bio"

        # Add a new entry to the dictionary
        data[encrypt(rec, self.unhashed_password)] = {
            "image": file_name,
            "message": encrypt(message, self.unhashed_password),
            "time": t,
            "about": encrypt(about, self.unhashed_password),
            "unread_messages": False,
            "user_id": idd
        }

        # Write the updated dictionary back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)

        user_data = {
            "text": rec,
            "secondary_text": message,
            "time": t,
            "image": file_name,
            "unread_messages": False,
            "user_id": idd
        }
        self.root.get_screen("home").chats.append(user_data)
        self.set_current("home")

        self.root.get_screen("home").ids.first.opacity = 0
        self.root.get_screen("home").ids.first.height = 0



        """
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')), 'r') as file:
            data = json.load(file)
        print(data)
        print(rec)
        print(self.unhashed_password)

        if rec == "":
            self.toast("Please enter a recipient")
            return

        for item in data:
            if decrypt(item, self.unhashed_password) == rec:
                self.toast("Already added.")
                # TODO: Make it so that you can enter an already used name and start a chat like that
                return

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.connect(conn)
        sock2.send(f"GET_ID:{rec}".encode())
        o = sock2.recv(1024)
        if o == b"error":
            self.toast("Invalid recipient.")
            return
        sock2.close()

        file_name = f'user_avatars/{o.decode()}.png'

        # Create a SHA256 hash object
        hash_object = hashlib.sha256()

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.connect(conn)
        sock2.settimeout(5)
        sock2.send(f"GET_AVATAR:{rec}".encode())

        with open(file_name, 'wb') as file:
            while True:
                try:
                    data = sock2.recv(4096)
                except:
                    break
                # print(data)
                if not data:
                    break
                if data == b"default":
                    file.write(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"default.jpg"), "rb").read())
                    break

                # Update the hash object with the received data
                hash_object.update(data)

                file.write(data)

        # Calculate the final SHA256 hash
        hash_value = hash_object.hexdigest()
        print("SHA256 hash:", hash_value)

        sock2.close()

        with open('assets/users.json', 'r') as file:
            data = json.load(file)

        # t = str(f"{datetime.now().strftime('%H:%M')}")
        t = "00:00"

        message = "test"
        about = "test bio"

        # Add a new entry to the dictionary
        data[encrypt(rec, self.unhashed_password)] = {
            "image": file_name,
            "message": encrypt(message, self.unhashed_password),
            "time": t,
            "about": encrypt(about, self.unhashed_password),
            "unread_messages": False,
            "user_id": o.decode()
        }

        # Write the updated dictionary back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)

        user_data = {
            "text": rec,
            "secondary_text": message,
            "time": t,
            "image": file_name,
            "unread_messages": False,
            "user_id": o.decode()
        }
        self.root.get_screen("home").chats.append(user_data)
        self.set_current("home")

        self.root.get_screen("home").ids.first.opacity = 0
        self.root.get_screen("home").ids.first.height = 0
        """

        # self.current_chat_with = rec
        # self.start_chat()
        # self.set_current("chat")

    def nah(self, touch, name):
        a, touch = touch
        if a.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                # Scrolling detected, ignore the touch event
                return
            self.is_touching = True
            self.long_press_trigger = Clock.schedule_once(partial(self.check_press_type, name), self.long_press_duration)

    def no(self, n, touch):
        if self.is_touching:
            if not n.collide_point(*touch.pos):
                self.cancel_press()

    def noo(self, n, touch, text):
        if self.is_touching:
            self.cancel_press()
            if n.collide_point(*touch.pos):
                print("Short press detected!")
                self.current_chat_with = text
                self.root.get_screen("home").goto_chat_screen(text)
                self.start_chat()
                print(text)

    def check_press_type(self, name, *args):
        if self.is_touching:
            print("Long press detected!")
            self.root.get_screen("home").user_settings(name)
            self.cancel_press()

    def cancel_press(self):
        self.is_touching = False
        if self.long_press_trigger:
            self.long_press_trigger.cancel()
            self.long_press_trigger = None

    def delete_user(self, user):
        print("I have never called that functin")
        # Read the JSON file
        with open('assets/users.json', 'r') as file:
            data = json.load(file)
        # Delete the entry with key "asd"
        if encrypt(user, self.unhashed_password) in data:
            del data[encrypt(user, self.unhashed_password)]

        # Write the updated data back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)

        self.root.get_screen("home").popup2.dismiss(force=True)

        with open('assets/users.json', 'r') as file:
            data = json.load(file)
        self.root.get_screen("home").chats = []
        if data != {}:
            for i in data:
                i_dec = decrypt(i, self.unhashed_password)
                user_data = {
                    "text": i_dec,
                    "secondary_text": decrypt(data[i]["message"], self.unhashed_password),
                    "time": data[i]["time"],
                    "image": data[i]["image"],
                    "name": i,
                    "unread_messages": data[i]["unread_messages"],
                }
                self.root.get_screen("home").chats.append(user_data)
        else:
            self.root.get_screen("home").ids.first.opacity = 1

        self.set_current("home")

    def signup(self, username, password):
        if username == "" or password == "":
            return
        # First with RSA, then with NTRU

        r = requests.post("http://api.protdos.com/user/exists", json={"username": username})
        if r.json()["exists"]:
            self.toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return

        if len(username) > 12:
            self.toast("Username too long.")
            return
        if " " in username:
            self.toast("No space allowed.")
            return

        # if hashCrackWordlist(password) is not None or strength_test(password)[0] is False:
        #     self.toast("Password isn't strong enough.")
        #     return
        # TODO Implement when released in production

        public, private = rsa.newkeys(1024)

        r = self.session.post("http://api.protdos.com/register", json={"username": username, "password": password, "public": public.save_pkcs1().decode()})
        print(r.json())

        if r.json()["code"] == 11110:
            print("Entry.")
            set_public_key(username, password, public.save_pkcs1().decode())
            set_private_key(username, password, private.save_pkcs1().decode())

            self.login(username, password, show=False)

        elif r.json()["code"] == 10009:
            self.toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return
        else:
            self.toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return


        """
        print("nah bruh")
        time.sleep(.5)
        sock.send(public.save_pkcs1())
        r = sock.recv(1024).decode()
        if r == "error":
            self.toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return
        elif r == "errorv2":
            self.toast("ID already used - internal error. Try again later.")
            return
        elif r == "errorv4":
            self.toast("Invalid username.")
            self.root.get_screen("auth").uname.shake()
            return

        self.private_key = private.save_pkcs1()
        self.public_key = public.save_pkcs1()

        self.username = username
        self.password = hash_pwd(password)
        self.unhashed_password = password



        # with open(f"private_key_{username}.txt", "w") as file:
        #     file.write(
        #         Encrypt(message_=private.save_pkcs1().decode(), key=password).encrypt().decode())
        # with open(f"public_key_{username}.txt", "w") as file:
        #     file.write(public.save_pkcs1().decode())
        set_public_key(username, password, public.save_pkcs1().decode())
        set_private_key(username, password, private.save_pkcs1().decode())

        # self.toast("Account created successfully!")

        self.login(username, password, show=False)
        """

    def do_request(self, method, url, json=None, session=None):
        if method == "GET":
            if session:
                return self.session.get(url, json=json)
            return requests.get(url, json=json)
        else:
            if session:
                print(url, json)
                return self.session.post(url, json=json)
            return requests.post(url, json=json)


    def login(self, username, password, show=True):
        threading.Thread(target=self.login2, args=(username, password,)).start()
    
    @mainthread
    def set_current(self, s):
        self.root.set_current(s)

    def login2(self, username, password):
        try:
            if username == "" or password == "":
                return
            r = concurrent.futures.ThreadPoolExecutor().submit(self.do_request, "POST", "http://api.protdos.com/login", {"username": username, "password": password}, self.session).result()
            print(r)

            # r = self.session.post("http://api.protdos.com/login", json={"username": username, "password": password})
            print(r.json())
            if r.json()["code"] == 10003:
                self.username = username
                self.unhashed_password = password
                self.password = hash_pwd(password)

                self.set_current("2fa_verify")

            elif r.json()["code"] == 11110:
                if username != "Google":
                    public = get_public_key(username, password)
                    private = get_private_key(username, password)
                    if public and private:
                        self.public_key = rsa.PublicKey.load_pkcs1(public)
                        self.private_key = rsa.PrivateKey.load_pkcs1(private)
                    else:
                        self.toast("Invalid credentials")
                        return
                else:
                    self.public_key = rsa.PublicKey.load_pkcs1(
                        b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
                    self.private_key = rsa.PrivateKey.load_pkcs1(
                        b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdrsaYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')
                self.username = username
                self.unhashed_password = password
                self.password = hash_pwd(password)
                idd = r.json()["id"]
                self.id = r.json()["id"]
                self.tries_left = 4

                print(self.public_key)

                self.avatar_path = "default.jpg" if not os.path.exists(
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 f"user_avatars/{idd}.png")) else os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{idd}.png")
                print("AVATAR_PATH:", self.avatar_path)
                self.set_current("home")
            else:
                if self.tries_left <= 3:
                    self.toast(f"Invalid. {self.tries_left} tries left.")
                else:
                    self.toast("Invalid credentials")
                self.root.get_screen("auth").uname.shake()
                self.root.get_screen("auth").password.shake()
                self.tries_left -= 1
                if self.tries_left <= 0:
                    self.tries_left = 4
                    delete_all()
                return
            """
            if r == "error":
                if self.tries_left <= 3:
                    self.toast(f"Invalid. {self.tries_left} tries left.")
                else:
                    self.toast("Invalid credentials")
                self.root.get_screen("auth").uname.shake()
                self.root.get_screen("auth").password.shake()
                # self.root.get_screen("auth").password.shake()
                self.tries_left -= 1
                if self.tries_left <= 0:
                    self.tries_left = 4
                    delete_all()
                return
            ################ obsolete ################
            # elif r == "errorv2":
            #     self.toast("Invalid password")
            #     self.root.get_screen("auth").password.shake()
            #     return
            elif r == "need_2fa_code":
                print("bebrerer")
                # TODO: 2DA Verificatino needed
                self.set_current("2fa_verify")

                self.username = username
                self.unhashed_password = password
                self.password = hash_pwd(password)

                pass
            else:
                if username != "Google":
                    #with open(f"private_key_{username}.txt", "r") as file:
                    #    a = file.read()
                    #    dec_priv = Decrypt(message_=a, key=password).decrypt().encode()
                    #    # print(dec_priv)
                    #    if dec_priv is None:
                    #        self.toast("Private key couldn't be decrypted.")
                    #        return
                    #    self.private_key = rsa.PrivateKey.load_pkcs1(dec_priv)
                    #with open(f"public_key_{username}.txt", "rb") as file:
                    #    a = file.read()
                    #    self.public_key = rsa.PublicKey.load_pkcs1(a)
                    public = get_public_key(username, password)
                    private = get_private_key(username, password)
                    if public and private:
                        self.public_key = rsa.PublicKey.load_pkcs1(public)
                        self.private_key = rsa.PrivateKey.load_pkcs1(private)
                    else:
                        self.toast("Invalid credentials")
                        return
                else:
                    self.public_key = rsa.PublicKey.load_pkcs1(
                        b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
                    self.private_key = rsa.PrivateKey.load_pkcs1(
                        b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdrsaYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')
                self.username = username
                self.unhashed_password = password
                self.password = hash_pwd(password)
                _, idd, has_2fa = r.split(":")
                self.id = idd
                self.tries_left = 4
                self.has_2fa = True if int(has_2fa) == 1 else False
                # self.toast("Logged in!")

                print(self.public_key)

                self.avatar_path = "default.jpg" if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{idd}.png")) else os.path.join(os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{idd}.png")
                print("AVATAR_PATH:", self.avatar_path)

                self.set_current("home")
            """
            # if show:
            #    self.toast("Signed In successfully!")
        except Exception as e:
            print(e)
            self.toast("Error signing in!")

    def send_message(self, text, uid):
        try:
            if not text:
                return

            print("a", self.current_chat_with)
            # self.root.get_screen("chat").ids.field.text = ""
            # self.root.get_screen("chat").scroll_to_bottom()

            enc_identity = rsa.encrypt(f"{self.username}---{self.id}".encode(), self.public_key_of_partner)
            enc = rsa.encrypt(text.encode(), self.public_key_of_partner)
            signature = rsa.sign(text.encode(), self.private_key, "SHA-256")


            d = {
                "message": str(enc),
                "recipient": self.current_chat_with,
                "signature": str(signature),
                "identity": str(enc_identity),
            }

            r = requests.post("http://api.protdos.com/send", json=d).json()
            print(r)

            if r["code"] != 11110:  # 11110
                delete_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)
                # self.root.get_screen("chat").ids.field.text = text
                # TODO: Not sure about this
                for item in self.root.get_screen("chat").ids.box.children:
                    if item.uid == uid:
                        item.icon = "error_outline"
                        item.icon_color = "#fc050d"
                        break
                self.toast("Error sending message...")
            else:
                for item in self.root.get_screen("chat").ids.box.children:
                    if item.uid == uid:
                        item.icon = "check_circle"
                        break
                print("Success")
        except:
            delete_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)
            for item in self.root.get_screen("chat").ids.box.children:
                if item.uid == uid:
                    item.icon = "error_outline"
                    item.icon_color = "#fc050d"
                    break
            self.toast("Error sending message...")

        """
        self.anonymous_socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.anonymous_socket_connection.connect(conn)

        self.anonymous_socket_connection.send(f"SEALED_PM:{current_chat_with}".encode())
        resp1 = self.anonymous_socket_connection.recv(1024).decode()
        if resp1.split(":")[0] == "received_request" and resp1.split(":")[1] == hash_obj(f"SEALED_PM:{current_chat_with}"):
            print("[+] [1/4] - Request is valid and hashes are matching")
            print("Continuing")
            for item in self.root.get_screen("chat").ids.box.children:
                if item.uid == uid:
                    item.icon = "check_circle"
                    break
            # self.root.get_screen("chat").chat_logs = get_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)

        else:
            delete_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)
            # self.root.get_screen("chat").chat_logs.get()
            self.toast("Error sending message...")
            return
        time.sleep(.5)

        print("Sending our encrypted identity")
        enc_identity = rsa.encrypt(f"{self.username}---{self.id}".encode(), self.public_key_of_partner)
        print("Encrypted identity:", enc_identity)
        self.anonymous_socket_connection.send(enc_identity)
        resp2 = self.anonymous_socket_connection.recv(1024).decode()
        if resp2 == "received_identity":
            print("[+] [2/4] - Data is valid")
            print("Continuing")

        enc = rsa.encrypt(text.encode(), self.public_key_of_partner)
        print("Encrypted message:", enc)
        time.sleep(.5)
        self.anonymous_socket_connection.send(enc)
        resp3 = self.anonymous_socket_connection.recv(1024).decode()
        if resp3 == "received_data":
            print("[+] [3/4] - Data is valid")
            print("Continuing")
        time.sleep(.5)

        signature = rsa.sign(text.encode(), self.private_key, "SHA-256")
        print("Signature of message: ", signature)

        encrypted_sign = split_and_process(signature, self.public_key_of_partner)
        print("Blocks: ", encrypted_sign)
        for block in encrypted_sign:
            self.anonymous_socket_connection.send(block)
            time.sleep(.5)
        print("Okay, sending final.")
        time.sleep(.5)
        self.anonymous_socket_connection.send(b"done")

        resp4 = self.anonymous_socket_connection.recv(1024).decode()
        if resp4 == "received_sign":
            print("[+] [4/4] - Signature is valid")
            print("Finished")

        self.last_sent = True
        """

    def change_avatar(self, *args):
        element = self.root.get_screen("user_settings").ids.profile_img
        if element.collide_point(*args[1].pos):
            filechooser.open_file(on_selection=self.selected, multiple=False)

    def selected(self, selection):
        if len(selection) == 0:
            return
        sel = selection[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = sel[sel.rfind('.'):].lower()
        t = file_extension in image_extensions
        if not t:
            self.toast("Unsupported ending.")
            return
        print(t)
        print(selection)

        r = self.session.post("http://api.protdos.com/change/avatar", files={"upload_file": open(sel, "rb")})
        print(r.json())

        if r.json()["code"] == 11110:
            with open(sel, 'rb') as file:
                image_data = file.read()
            pp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{self.id}.png")

            with open(pp, "wb") as file:
                file.write(image_data)

            shutil.copy(sel, pp)
            self.avatar_path = sel
            self.root.get_screen("user_settings").avatar_path = sel
            self.root.get_screen("user_settings").av(sel)

            # self.toast("Updated.")
            return
        else:
            self.toast("Couldn't send file.")
            return

    def start_chat(self):
        rec = self.current_chat_with
        r = self.session.post("http://api.protdos.com/user/id", json={"recipient": rec}).json()
        print(r)
        if r["code"] != 11110:
            self.toast("Invalid recipient.")
            return
        print(rec)

        idd = r["id"]

        r = self.session.post("http://api.protdos.com/user/public", json={"id": idd})
        print(r.content)

        public = rsa.PublicKey.load_pkcs1(r.content)
        print("Loaded key of rec:", public)
        self.public_key_of_partner = public

        # TODO: Fix open statements (do it from absolute path)

        try:
            if rec not in open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "r").read():
                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "a") as rec_file:
                    # rec_file.write(rec + "\n")
                    rec_file.write(Encrypt(message_=rec, key=self.unhashed_password).encrypt().decode() + "\n")
            open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "r").close()
        except:
            open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "w").close()
            with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "a") as rec_file:
                rec_file.write(Encrypt(message_=rec, key=self.unhashed_password).encrypt().decode() + "\n")
            open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats/private_chats.csv')), "r").close()

        self._stop_event = threading.Event()
        t = threading.Thread(target=self.receive_messages_private, args=(public,))
        self.message_thread = t
        self.message_thread.start()

    @mainthread
    def open_warning(self, mess):
        self.root.get_screen("chat").open_warning(mess=mess.decode())

    def receive_messages_private(self, _):
        print("Started...")
        while not self._stop_event.is_set():
            try:
                res = self.session.post(f"http://api.protdos.com/receive")
                print(res.json())
                if res.json()["code"] == 11110:
                    for message in res.json()["messages"]:
                        print(message)

                        full_sign = eval(message["signature"])
                        sealed_sender = eval(message["identity"])
                        enc_message = eval(message["message"])


                        print("-" * 20)
                        print(sealed_sender)
                        sender = rsa.decrypt(sealed_sender, self.private_key)
                        print(sender)
                        print("")
                        print(message)
                        dec_message = rsa.decrypt(enc_message, self.private_key)
                        print(dec_message)
                        print("")
                        print(full_sign)

                        print(dec_message, full_sign, sender)

                        try:
                            rsa.verify(dec_message, full_sign, self.public_key_of_partner)
                        except Exception as e:
                            self.open_warning(dec_message)
                            print(e)
                            print("No verification")

                        self.add_resp(dec_message.decode())

            except Exception as e:
                print(e)
                print("Not established yet")
            time.sleep(2)  # TODO: Change this to much lower
        print("Stopped.")

    @mainthread
    def add_resp(self, text):
        self.root.get_screen("chat").ids.box.add_widget(
            ChatBubble2(text=extract_links(text), send_by_user=False, icon="check_circle"))

    #def receive_messages_private(self, _):
    #    _ = self.current_socket.recv(1024)
    #    while True:
    #        try:
    #            print("-"*50)
    #            message = self.current_socket.recv(1024)
    #            print(message)
    #            try:
    #                if "---" in message.decode():
    #                    message = self.current_socket.recv(1024)
    #                    print(message)
    #            except Exception as e:
    #                print(e)
    #                print("nasd")
    #            if message:
    #                dec = rsa.decrypt(message, self.private_key)
    #                print(dec)
    #                signature = self.current_socket.recv(1024)
    #                print(signature)
    #                print(self.public_key_of_partner)
#
    #                self.root.get_screen("chat").chat_logs.append(
    #                    {
    #                        "text": dec.decode(),
    #                        "send_by_user": False,
    #                    }
    #                )
#
    #                try:
    #                    rsa.verify(dec, signature, self.public_key_of_partner)
    #                    print("Verification success!")
    #                except Exception as e:
    #                    self.open_warning(dec)
    #                    print(e)
    #                    print("Failed verification.")
#
    #        except Exception as e:
    #            print(e)
    #            break

    def close_chat(self):
        self.set_current("home")
        threading.Thread(target=self.close_chat_2).start()

    def close_chat_2(self):
        try:
            self.stop_thread()
            self.message_thread.join()
        except:
            pass
        self.close_chat3()

    @mainthread
    def close_chat3(self):
        self.root.get_screen("chat").ids.box.clear_widgets()
        self.root.get_screen("chat").chat_logs = []


    def nothing(self):
        pass

    def done_change(self):
        self.root.get_screen("settings").l.dismiss(force=True)

    def notify(self, title, message, icon_path=r"images\logo.png"):
        notification(
            title=title,
            message=message,
            app_icon=icon_path,
            timeout=30
        )

    def change_password(self, old, new):
        print(old, new, self.unhashed_password)
        if old != self.unhashed_password:
            self.toast("Current Password is wrong.")
            return

        r = self.session.post("http://api.protdos.com/change/password", json={"new": new, "old": old})
        print(r.json())

        if r.json()["code"] == 11110:
            self.password = hash_pwd(new)
            self.unhashed_password = new

            set_private_key(self.username, new, self.private_key.save_pkcs1().decode())
            set_public_key(self.username, new, self.public_key.save_pkcs1().decode())

            self.root.get_screen("user_settings").d.dismiss(force=True)
            self.toast("Password changed.")
            return
        else:
            self.toast("Something went wrong.")
            return

    def change_username(self, uname):
        r = self.session.post("http://api.protdos.com/change/username", json={"new": uname})
        print(r.json())

        if r.json()["code"] == 11110:
            self.username = uname
            self.username_test = StringProperty("NEWEW")

            set_private_key(uname, self.unhashed_password, self.private_key.save_pkcs1().decode())
            set_public_key(uname, self.unhashed_password, self.public_key.save_pkcs1().decode())

            self.root.get_screen("user_settings").d2.dismiss(force=True)
            self.toast("Username changed.")
            return
        else:
            self.toast("Something went wrong.")
            return

    def switch_language(self, lang):
        print("-----------")
        print(lang)
        lang_to_id = config.lang_to_code(lang)
        print(lang_to_id)
        if config.get_language() == lang_to_id:
            print("nah")
            return
        config.set_language(lang_to_id)
        print("-----------")

        self.language = str(lang_to_id).upper()

    def translate(self, text):
        print("TEXT: ", text)
        c = config.get_language()
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/translations.json')), "r") as file:
            j = json.load(file)
        try:
            t = j["translations"][str(c)][text]
            print("skipped")
            return t
        except:
            t = GoogleTranslator(source='en', target=c).translate(text=text)
            j["translations"][str(c)][text] = t
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/translations.json'), "w") as file:
                json.dump(j, file, indent=4)
            return t

    def is_name_taken(self, name):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json'), 'r') as file:
            data = json.load(file)
        return encrypt(name, self.unhashed_password) in data

    def block_user(self):
        user = self.current_chat_with

        self.socket_connection.send(f"BLOCK:{user}:{self.username}:{self.password}".encode())
        res = self.socket_connection.recv(1024).decode()
        print(res)
        if res == "success":
            self.toast("User is blocked")
            return
        self.toast("An error occurred")

    def enable_2fa(self):
        # TODO: Implement
        if self.has_2fa:
            self.set_current("disable_2fa")
        else:
            r = self.session.post("http://api.protdos.com/2fa/enable", json={"username": self.username, "password": self.unhashed_password})
            out = r.json()
            print(out)
            secret_key = out["secret_key"]
            rr = pyotp.totp.TOTP(secret_key).provisioning_uri(name=f'Veilo - {self.username}', issuer_name='Veilo')
            q = qrcode.make(rr)
            q.save("2fa_code.png")
            self.set_current("enable_2fa")

    def verify_2fa(self, code):
        print("yea")
        if self.has_2fa:
            print("wtf")
            return

        self.has_2fa = True

        # self.socket_connection.send(f"2FA_VERIFY:{code}:{self.username}:{self.password}".encode())
        # r = self.socket_connection.recv(1024).decode()
        print(self.username, self.unhashed_password)
        r = self.session.post("http://api.protdos.com/2fa/verify", json={"username": self.username, "password": self.unhashed_password, "code": code})
        print(r)
        if r.json()["code"] != 11110:
            self.toast("Error verifying 2fa")
            self.set_current("auth")
            return
        # r = self.session.post("http://api.protdos.com/login", json={"username": self.username, "password": self.unhashed_password, "code": code})

        print(self.username)
        print(self.password)
        print(self.unhashed_password)

        if self.username != "Google":
            with open(f"private_key.txt", "r") as file:
                a = file.read()
                dec_priv = a
                # print(dec_priv)
                if dec_priv is None:
                    self.toast("Private key couldn't be decrypted.")
                    return
                self.private_key = rsa.PrivateKey.load_pkcs1(dec_priv.encode())
            with open(f"public_key.txt", "rb") as file:
                a = file.read()
                self.public_key = rsa.PublicKey.load_pkcs1(a)
        else:
            self.public_key = rsa.PublicKey.load_pkcs1(
                b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
            self.private_key = rsa.PrivateKey.load_pkcs1(
                b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdrsaYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')

        self.set_current("home")

    def disable_2fa(self, code):
        self.socket_connection.send(f"2FA_DISABLE:{self.username}:{self.password}:{code}".encode())
        r = self.socket_connection.recv(1024).decode()
        if r == "error":
            self.toast("Error disabling 2fa")
            return
        self.set_current("home")

    def file_chooser(self):
        try:
            filechooser.open_file(on_selection=self.selected_file)
        except:
            pass

    def get_image_size(self, image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                return width, height
        except Exception as e:
            return None

    def selected_file(self, selection):
        try:
            print(selection[0])
            if is_image_file(selection[0]):
                self.root.get_screen("chat").ids.box.add_widget(ImageMessage(source=selection[0], send_by_user=True, file_size=self.get_image_size(selection[0])))
            elif is_audio_file(selection[0]):
                siz = create_loudness_intervals(selection[0])
                self.root.get_screen("chat").ids.box.add_widget(AudioMessage(send_by_user=True))
            else:
                print("YYYY")
                self.root.get_screen("chat").ids.box.add_widget(Attachment(send_by_user=True, filename=os.path.basename(selection[0]), file_size=get_file_size(selection[0]), source_=selection[0]))
        except Exception as e:
            print(e)
            pass

    def on_stop(self):
        self.socket_connection.close()

    def on_pause(self):
        return True

    def update_main(self, color):
        self.root.get_screen("theming").main_color = color
        self.root.get_screen("theming").update_main()

    def update_sec(self, color):
        self.root.get_screen("theming").secondary_color = color
        self.root.get_screen("theming").update_sec()

    def update_picker(self, color):
        self.root.get_screen("theming").picker_color = color

    def open_link(self, message_id, link):
        self.root.get_screen("chat").open_link_warning(link)
        # webbrowser.open(link)

    def dismiss(self):
        self.root.get_screen("chat").warn.dismiss(force=True)

    def dismiss2(self):
        self.root.get_screen("other").d.dismiss(force=True)

    def delete_account(self):
        self.set_current("auth")

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(conn)
        sk.send(f"DELETE_ACCOUNT:{self.password}:{self.username}".encode())
        sk.close()

        try:
            self.socket_connection.close()
        except:
            pass
        try:
            self.anonymous_socket_connection.close()
        except:
            pass

        a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), "w")
        a.write("{}")
        a.close()

        self.stop()

        raise Exception("Stopping Program")

    def detect_breaches(self, email, phone):
        r = requests.post("http://api.protdos.com/breach", json={"email": email, "phone": phone})
        print(r.json())

        if r.json()["code"] == 11110:
            print("Yup")
            self.toast("Added.")
            self.root.get_screen("user_settings").b.dismiss(force=True)
            return
        elif r.json()["code"] == 10015:
            self.toast("Invalid phone Format.")
            return
        elif r.json()["code"] == 10016:
            self.toast("Invalid email Format.")
            return
        self.toast("Error occurred.")

    def open_file(self, file_path):
        max_width, max_height = Window.size
        faktor = .86
        max_width = max_width * faktor
        max_height = max_height * faktor


        image = Image.open(file_path)

        # Get the original dimensions
        original_width, original_height = image.size

        # Calculate the new dimensions to maintain the aspect ratio
        width, height = original_width, original_height
        if original_width > max_width:
            width = max_width
            height = int(max_width / original_width * original_height)
        if height > max_height:
            height = max_height
            width = int(max_height / original_height * original_width)

        print(original_width, original_height)
        print(width, height)
        """
        file_size = self.get_image_size(file_path)

        width, height = file_size
        faktor = .3
        target_width, target_height = Window.size
        new_width, new_height = resize_image(original_width=width, original_height=height,
                                             target_width=target_width * faktor, target_height=target_height * faktor)
        file_size = new_width, new_height

        print(file_size)

        if file_size[0] > 245:
            file_size[0] = 245
            file_size[1] = 245 / file_size[0] * file_size[1]

        print((width, height), file_size)
        """

        self.root.get_screen("chat").open_preview(file_path, size=(width, height))

    def download_file(self, path):
        try:
            print(path)
            filename = os.path.basename(path)
            print(filename)
            Image.open(path).save(f"{str(uuid.uuid4())}_{filename}")
            # urllib.request.urlretrieve(path, filename)
            self.toast("Downloaded.")
        except:
            print("Not an image.")
            # TODO: Do this for not-image too

    def check_pull_refresh(self, view, grid):
        """Check the amount of overscroll to decide if we want to trigger the
        refresh or not.
        """
        # max_pixel = dp(200)
        # to_relative = max_pixel / (grid.height - view.height)
        # print(to_relative)
        # print(max_pixel, grid.height, view.height, view.scroll_y)
        # if view.scroll_y <= 1.0 or self.refreshing:
        #     return
#
        # self.refresh_data()

        # TODO: Implement / FIX this.
        return

        if view.scroll_y < 0.7:
            if not self.refreshing:
                self.refresh_data()
                print("Yewah")

    def refresh_data(self):
        self.refreshing = True
        threading.Thread(target=self._refresh_data).start()

    @mainthread
    def cll(self):
        self.root.get_screen("home").ids.grid.clear_widgets()
        self.root.get_screen("home").chats = []
        # Clock.schedule_once(self.root.get_screen("home").load_all, 0)

    def _refresh_data(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "users.json"), "r") as f:
            data = json.load(f)

        ps = self.unhashed_password

        chats = []

        if data != {}:
            for i in data:
                i_dec = decrypt(i, ps)
                if i_dec is not None:
                    user_data = {
                        "text": i_dec,
                        "time": data[i]["time"],
                        "image": data[i]["image"],
                        "name": i,
                        "message": data[i]["message"],
                        "user_id": data[i]["user_id"],
                        "about": data[i]["about"],
                        "unread_messages": data[i]["unread_messages"],
                    }
                    chats.append(user_data)
                else:
                    user_data = {
                        "time": data[i]["time"],
                        "image": data[i]["image"],
                        "name": i,
                        "message": data[i]["message"],
                        "user_id": data[i]["user_id"],
                        "about": data[i]["about"],
                        "unread_messages": data[i]["unread_messages"],
                    }
                    chats.append(user_data)
        print(chats)

        for item in chats:
            try:
                name = item["text"]
                idd = requests.post("http://api.protdos.com/user/id", json={"recipient": name}).json()["id"]
                r = requests.post("http://api.protdos.com/user/avatar", json={"id": idd})
                file_name = f'user_avatars/{idd}.png'
                item["image"] = f'user_avatars/{idd}.png'
                with open(file_name, "wb") as f:
                    f.write(r.content)
            except:
                pass

        print(chats)

        # TODO: Write to file & live update in homescreen (call functino again)?

        # TODO: Update for Nw messages

        """
        data[encrypt(rec, self.unhashed_password)] = {
            "image": file_name,
            "message": encrypt(message, self.unhashed_password),
            "time": t,
            "about": encrypt(about, self.unhashed_password),
            "unread_messages": False,
            "user_id": idd
        }

        # Write the updated dictionary back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)
            
    user_data = {
                "text": i_dec,
                "time": data[i]["time"],
                "image": data[i]["image"],
                "name": i,
                "message": data[i]["message"],
                "user_id": data[i]["user_id"],
                "unread_messages": data[i]["unread_messages"],
            }
        """

        self.add_data()

        d = {}
        for item in chats:
            print(item)
            d[item["name"]] = {
                "image": item["image"],
                "message": item["message"],
                "time": item["time"],
                "about": item["about"],
                "unread_messages": False,
                "user_id": item["user_id"]
            }
        print("\n")
        print(d)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "users.json"), "w") as file:
            json.dump(d, file, indent=4)

        self.cll()

        # Now adding back.

        data = d

        print(data)

        if data != {}:
            for i in data:
                i_dec = decrypt(i, ps)
                if i_dec is not None:
                    print(data[i]["image"])
                    user_data = {
                        "text": i_dec,
                        "secondary_text": decrypt(data[i]["message"], ps),
                        "time": data[i]["time"],
                        "image": data[i]["image"],
                        "name": i,
                        "unread_messages": data[i]["unread_messages"],
                    }
                    self.root.get_screen("home").chats.append(user_data)
            if len(self.root.get_screen("home").chats) == 0:
                self.root.get_screen("home").ids.first.opacity = 1
                self.root.get_screen("home").text_hidden = "1"
        else:
            self.root.get_screen("home").ids.first.opacity = 1
            self.root.get_screen("home").text_hidden = "1"


    @mainthread
    def add_data(self):
        self.refreshing = False


if __name__ == "__main__":
    PurpApp().run()
