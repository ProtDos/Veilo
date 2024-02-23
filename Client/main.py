import json
import os
import sys
import time
import traceback
import pyotp
import qrcode
import rsa
from jnius import cast
from PIL import Image
from plyer import notification
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from datetime import datetime
from extensions.key_saver import *
import requests
import shutil
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, OptionProperty, DictProperty
from kivy.clock import Clock, mainthread
from functools import partial
from plyer import filechooser
from extensions.security import *
import threading
from deep_translator import GoogleTranslator

root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(root_dir, "libs", "applibs"))
sys.path.insert(0, os.path.join(root_dir, "libs", "uix"))

# This is shown as an error, even though it is not, as sys changed the path of the file.
from components.chat_bubble import ImageMessage
from components.chat_bubble import Attachment
from components.chat_bubble import AudioMessage
from components.chat_bubble import ChatBubble2
from androspecific import statusbar
from core.theming import ThemeManager
from root import Root
from utils.configparser import config
from components.toast import toast
from core.encryption import encrypt, decrypt


if platform != "android":
    Window.size = (350, 650)
else:
    from android.permissions import request_permissions, Permission
    from android.permissions import check_permission
    from android.storage import primary_external_storage_path
    from android.runnable import run_on_ui_thread
    from android import mActivity as mA
    from jnius import autoclass
    from kivy.app import App
    from kivy.properties import DictProperty
    from kivy.properties import ObjectProperty
    from pushyy import Pushyy
    from pushyy import RemoteMessage

    try:

        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
        LinearLayout = autoclass('android.widget.LinearLayout')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        KeyEvent = autoclass('android.view.KeyEvent')
        EditText = autoclass('android.widget.EditText')
        InputType = autoclass('android.text.InputType')
        ViewGroup = autoclass('android.view.ViewGroup')
    except Exception as e:
        print(f"[ERROR]: {traceback.format_exc()}")


def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff']
    _, extension = os.path.splitext(file_path)
    return extension.lower() in image_extensions


def is_audio_file(file_path):
    audio_extensions = [".wav", ".mp3"]
    _, extension = os.path.splitext(file_path)
    return extension.lower() in audio_extensions


def extract_links(text):
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
    suffix = "[/color][/ref]"
    links = re.findall(url_pattern, text)
    modified_text = text
    for link in links:
        modified_link = f"[ref={link}][color=#0000EE]" + link + suffix
        modified_text = modified_text.replace(link, modified_link)

    return modified_text


def delete_dict_by_uid(lst, uid):
    for item in lst:
        if item.get("idd") == uid:
            lst.remove(item)
            return True
    return False


def get_dict_by_uid(lst, uid):
    for item in lst:
        if item.get("idd") == uid:
            item["icon"] = "check_circle"
            return lst
    return lst


def convert_bytes(size, unit="B"):
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
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

    if aspect_ratio > 1:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    return [new_width, new_height]


def change_avatar():
    pass


def delete_all():
    a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), "w")
    a.write("{}")
    a.close()

    script_path = os.path.abspath(__file__)
    files = os.listdir(script_path)

    for file_name in files:
        if "_key_" in file_name:
            file_path = os.path.join(script_path, file_name)
            os.remove(file_path)
            print(f"Deleted: {file_path}")

    r = App.get_running_app().session.post(App.get_running_app().api_url + "/account/delete")
    print(r.json())

    return True


def read_mailboxes():
    with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mailboxes.json')), 'r') as file:
        data = json.load(file)
    return data.get('mailboxes', [])


def add_mailbox(mailbox):
    mailboxes = read_mailboxes()
    mailboxes.append(mailbox)
    with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mailboxes.json')), 'w') as file:
        json.dump({"mailboxes": mailboxes}, file, indent=4)



if platform == "android":
    def my_token_callback(token):
        print(token)
        App.get_running_app().device_token = token
        return token


    def my_foreground_callback(data: RemoteMessage):
        print("my_foreground_callback")
        print(data)
        App.get_running_app().recent_notification_data = data.as_dict()
        App.get_running_app().receive_notify()


    def my_notification_click_callback(data: RemoteMessage):
        print("my_notification_click_callback")
        print(data)
        App.get_running_app().recent_notification_data = data.as_dict()


    def new_token_callback(data):
        print("new_token_callback")
        print(data)
        App.get_running_app().device_token = data


class VeiloApp(App):
    recent_notification_data = DictProperty(rebind=True)

    theme_cls = ThemeManager()
    trans = ObjectProperty()
    settings = ObjectProperty()
    refreshing = BooleanProperty(False)
    is_still_up = False

    device_token = None

    default_view_height = 0

    my_file_path = __file__

    wwwindow = Window

    language = OptionProperty(config.get_language().upper(), options=(
        'EN', 'DE', "ES", "FR", "ZH", "AR", "BN", "RU", "PT", "UR", "ID", "JA", "SW", "PA"))
    show_message_content = BooleanProperty(config.message_opt())

    pause_event = threading.Event()
    pause_event.set()
    is_running = True
    in_chat = False

    buffer_messages = []
    KeyStore = None
    context = None
    
    api_url = "http://api.protdos.com"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._stop_event = threading.Event()
        self.message_thread = threading.Thread()

        self.title = "Veilo"
        self.icon = "assets/images/logo.png"

        self.theme_cls.theme_style = config.get_theme_style()

        Window.keyboard_anim_args = {"d": 0.2, "t": "in_out_expo"}  # linear
        Window.softinput_mode = "below_target"

        self.long_press_duration = 0.15  # Adjust this value to change the long press duration
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

        self.current_socket = None

        self.public_key_of_partner = None

        self.last_sent = True

        self.avatar_path = "default.jpg" if not os.path.exists(f"user_avatars/{self.id}") else f"user_avatars/{self.id}"

        self.tries_left = 4

        self.session = requests.Session()
        self.mailbox = 0
        self.mailbox_key = 0

    @staticmethod
    def get_token():
        return Pushyy().get_device_token(my_token_callback)

    def build(self):
        try:
            self.icon = r"assets/images/logo.png"
            self.root = Root()
            c = config.is_startup()
            if c != "False":
                self.root.set_current("startup")
            else:
                self.root.set_current("auth")
        except Exception as e:
            print(f"[ERROR]: {traceback.format_exc()}")

    """
        These functions are for saving / loading our private and public keys to the android keystorage
    """
    if platform == "android":
        @run_on_ui_thread
        def set_to_keystore(self, message: str, alias: str):
            print(self.KeyStore)
            print(self.context)
            print(alias)
            self.KeyStore.generateKeyPair(self.context, alias)
            enc = self.KeyStore.saveEncryptedText(self.context, message, alias)
            print(enc)
            return enc

        @run_on_ui_thread
        def load_from_keystore(self, encrypted: str, alias: str):
            dec = self.KeyStore.getDecryptedText(self.context, encrypted, alias)
            print(dec)
            return dec


    def check_for_messages_on_home_screen(self):
        while self.is_running:
            try:
                self.pause_event.wait()
                res = self.session.post(self.api_url + "/receive")
                print(f"    [DEBUG] (check_for_messages_on_home_screen) - {res.json()}")
                if res.json()["code"] == 11110:
                    for message in res.json()["messages"]:
                        if not message.get("file"):
                            try:
                                _ = self.root.get_screen("home").chats
                                _ = self.root.get_screen("home").data
                            except:
                                pass

                            full_sign = eval(message["signature"])
                            sealed_sender = eval(message["identity"])
                            enc_message = eval(message["message"])

                            print(self.private_key)

                            sender = rsa.decrypt(sealed_sender, self.private_key)
                            dec_message = rsa.decrypt(enc_message, self.private_key)

                            self.buffer_messages.append({"sender": sender, "dec_message": dec_message, "full_sign": full_sign})

                            # Getting this error: (Fix needed)
                            # Unable to decode stream: java.io.FileNotFoundException: /data/data/org.test.myapp/files/app/assets\images\logo.ico: open failed: ENOENT (No such file or directory)

                            try:
                                if self.show_message_content:
                                    if platform == "android":
                                        notification.notify(
                                            title="New Message",
                                            message=f"{sender.decode().split('---')[0]}: {dec_message.decode()}",
                                            app_icon=os.path.join(
                                                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             r'assets/images/logo.ico')),
                                            timeout=30
                                        )
                                    else:
                                        notification.notify(
                                            title="New Message",
                                            message=f"{sender.decode().split('---')[0]}: {dec_message.decode()}",
                                            app_icon=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                               r'assets\images\logo.ico')),
                                            timeout=30
                                        )
                                else:
                                    if platform == "android":
                                        notification.notify(
                                            title="New Message",
                                            message=f"You have received a new message. Tap here to view!",
                                            app_icon=os.path.join(
                                                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             r'assets/images/logo.ico')),
                                            timeout=30
                                        )
                                    else:
                                        notification.notify(
                                            title="New Message",
                                            message=f"You have received a new message. Tap here to view!",
                                            app_icon=os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                               r'assets\images\logo.ico')),
                                            timeout=30
                                        )
                            except Exception:
                                print("     [ERROR] Couldn't send notification.")

                            user_in_contacts = False

                            for item in self.root.get_screen("home").ids.aaaa.data:
                                if item["text"] == sender.decode().split('---')[0]:
                                    item["unread_messages"] = True
                                    user_in_contacts = True
                                    break

                            if not user_in_contacts:
                                rec = sender.decode().split('---')[0]
                                try:
                                    idd = requests.post(self.api_url + "/user/id", json={"recipient": rec}).json()["id"]
                                except Exception as _:
                                    return


                                r = self.session.post(self.api_url + "/user/avatar", json={"id": idd})
                                display_name = self.session.post(self.api_url + "/user/display", json={"id": idd}).json()["display_name"]
                                public = self.session.post(self.api_url + "/user/public", json={"id": idd}).text

                                file_name = f'user_avatars/{idd}.png'

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'user_avatars/{idd}.png')), "wb") as f:
                                    f.write(r.content)

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')), 'r') as file:
                                    data = json.load(file)

                                t = str(f"{datetime.now().strftime('%H:%M')}")

                                secondary_text = rec
                                about = "*No Bio Available*"

                                data[encrypt(rec, self.unhashed_password)] = {
                                    "image": file_name,
                                    "message": encrypt(secondary_text, self.unhashed_password),
                                    "time": t,
                                    "about": encrypt(about, self.unhashed_password),
                                    "unread_messages": False,
                                    "user_id": idd,
                                    "public": str(public),
                                    "display": display_name
                                }

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')), 'w') as file:
                                    json.dump(data, file, indent=4)

                                user_data = {
                                    "text": rec,
                                    "secondary_text": secondary_text,
                                    "time": t,
                                    "image": file_name,
                                    "unread_messages": True,
                                    "user_id": idd,
                                    "public": str(public),
                                    "about": about,
                                    "display": display_name
                                }

                                print(user_data)

                                self.root.get_screen("home").chats.append(user_data)
                                Clock.schedule_once(self.update_text, 0)

                            self.root.get_screen("home").ids.aaaa.refresh_from_data()
                        else:
                            notification.notify(
                                title="New Message",
                                message=f"Attachment",
                                app_icon=os.path.join(
                                    os.path.join(os.path.dirname(os.path.abspath(__file__)), r'assets\images\logo.ico')),
                                timeout=30
                            )
            except Exception as e:
                print(f"        [ERROR] (check_for_messages_on_home_screen) {e}")
                print(traceback.format_exc())
            time.sleep(5)

    def update_text(self, _):
        self.root.get_screen("home").text_hidden = "0"

    def receive_notify(self):
        print("Yeah")
        if not self.in_chat:
            try:
                res = self.session.post(self.api_url + "/receive")
                print(f"    [DEBUG] (receive_notify) - {res.json()}")
                if res.json()["code"] == 11110:
                    for message in res.json()["messages"]:
                        if not message.get("file"):

                            try:
                                _ = self.root.get_screen("home").chats
                                _ = self.root.get_screen("home").data
                            except:
                                pass

                            full_sign = eval(message["signature"])
                            sealed_sender = eval(message["identity"])
                            enc_message = eval(message["message"])

                            print(self.private_key)

                            sender = rsa.decrypt(sealed_sender, self.private_key)
                            dec_message = rsa.decrypt(enc_message, self.private_key)

                            self.buffer_messages.append(
                                {"sender": sender, "dec_message": dec_message, "full_sign": full_sign})

                            try:
                                if self.show_message_content:
                                    if platform == "android":
                                        notification.notify(
                                            title="New Message",
                                            message=f"{sender.decode().split('---')[0]}: {dec_message.decode()}",
                                            app_icon=os.path.join(
                                                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             r'assets/images/logo.ico')),
                                            timeout=30
                                        )
                                    else:
                                        notification.notify(
                                            title="New Message",
                                            message=f"{sender.decode().split('---')[0]}: {dec_message.decode()}",
                                            app_icon=os.path.join(
                                                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             r'assets\images\logo.ico')),
                                            timeout=30
                                        )
                                else:
                                    if platform == "android":
                                        # print(os.path.join(
                                        #         os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        #                      r'assets/images/logo.ico')))
                                        # TODO: Fix this part
                                        notification.notify(
                                            title="New Message",
                                            message=f"You have received a new message. Tap here to view!",
                                            # app_icon=os.path.join(
                                            #     os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            #                  r'assets/images/logo.ico')),
                                            timeout=30
                                        )
                                    else:
                                        notification.notify(
                                            title="New Message",
                                            message=f"You have received a new message. Tap here to view!",
                                            app_icon=os.path.join(
                                                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             r'assets\images\logo.ico')),
                                            timeout=30
                                        )
                            except Exception:
                                print(traceback.format_exc())
                                print("     [ERROR] Couldn't send notification 2.")

                            user_in_contacts = False

                            for item in self.root.get_screen("home").ids.aaaa.data:
                                if item["text"] == sender.decode().split('---')[0]:
                                    item["unread_messages"] = True
                                    user_in_contacts = True
                                    break

                            if not user_in_contacts:
                                rec = sender.decode().split('---')[0]
                                try:
                                    idd = requests.post(self.api_url + "/user/id", json={"recipient": rec}).json()["id"]
                                except Exception as _:
                                    return

                                r = self.session.post(self.api_url + "/user/avatar", json={"id": idd})
                                display_name = self.session.post(self.api_url + "/user/display", json={"id": idd}).json()["display_name"]
                                public = self.session.post(self.api_url + "/user/public", json={"id": idd}).text

                                file_name = f'user_avatars/{idd}.png'

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'user_avatars/{idd}.png')), "wb") as f:
                                    f.write(r.content)

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')), 'r') as file:
                                    data = json.load(file)

                                t = str(f"{datetime.now().strftime('%H:%M')}")

                                secondary_text = rec
                                about = "*No Bio Available*"

                                data[encrypt(rec, self.unhashed_password)] = {
                                    "image": file_name,
                                    "message": encrypt(secondary_text, self.unhashed_password),
                                    "time": t,
                                    "about": encrypt(about, self.unhashed_password),
                                    "unread_messages": False,
                                    "user_id": idd,
                                    "public": str(public),
                                    "display": display_name
                                }

                                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json')), 'w') as file:
                                    json.dump(data, file, indent=4)

                                user_data = {
                                    "text": rec,
                                    "secondary_text": secondary_text,
                                    "time": t,
                                    "image": file_name,
                                    "unread_messages": True,
                                    "user_id": idd,
                                    "public": str(public),
                                    "about": about,
                                    "display": display_name
                                }

                                print(user_data)

                                self.root.get_screen("home").chats.append(user_data)

                                self.root.get_screen("home").text_hidden = "0"

                            self.root.get_screen("home").ids.aaaa.refresh_from_data()
                        else:
                            notification.notify(
                                title="New Message",
                                message=f"Attachment",
                                app_icon=os.path.join(
                                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 r'assets\images\logo.ico')),
                                timeout=30
                            )
            except Exception as e:
                print(f"     [DEBUG] (receive_notify) Error: {e}")
                print(traceback.format_exc())

    def pause_thread2(self):
        self.pause_event.clear()

    def resume_thread2(self):
        self.pause_event.set()

    def stop_thread2(self):
        self.is_running = False
        self.resume_thread2()

    def stop_thread(self):
        self._stop_event.set()

    if platform == "android":
        @run_on_ui_thread
        def on_start(self):
            try:
                statusbar.set_color(self.theme_cls.primary_color)
    
                Pushyy().foreground_message_handler(my_foreground_callback)
                Pushyy().notification_click_handler(my_notification_click_callback)
                Pushyy().token_change_listener(new_token_callback)
    
                self.get_token()
    
                print(self.device_token)
    
                # TODO: For Release: ENABLE THIS
                # LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                # window = mA.getWindow()
                # params = window.getAttributes()
                # params.setDecorFitsSystemWindows = False
                # params.layoutInDisplayCutoutMode = LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                # window.setAttributes(params)
                # window.setFlags(LayoutParams.FLAG_SECURE, LayoutParams.FLAG_SECURE)
                # window.addFlags(LayoutParams.FLAG_SECURE)
    
                # Not quite sure if this works
                EditorInfo = autoclass("android.view.inputmethod.EditorInfo")
                editText = EditText(activity)
                editorInfo = EditorInfo()
                editorInfo.imeOptions |= EditorInfo.IME_FLAG_NO_PERSONALIZED_LEARNING
                editText.setImeOptions(editorInfo.imeOptions)
            except Exception as e:
                print(f"[ERROR]: {traceback.format_exc()}")
    else:
        def on_start(self):
            statusbar.set_color(self.theme_cls.primary_color)

    def destroy_pop(self, _):
        try:
            self.root.get_screen("home").popup.dismiss(force=True)
        except Exception as e:
            print(f"[ERROR]: {traceback.format_exc()}")

    @mainthread
    def toast(self, message):
        toast(message)

    @mainthread
    def create_chat(self, rec):
        self.root.get_screen("home").popup.dismiss(force=True)
        Clock.schedule_once(partial(self.create_chat_0, rec), 0.1)

    def create_chat_0(self, rec, *_):
        if rec == "":
            self.root.get_screen("home").popup.content.ids.recipient.foreground_color = [255, 0, 0, 0.9]
            return self.toast("Please enter a recipient")

        r = self.session.post(self.api_url + "/user/id", json={"recipient": rec}).json()
        if r["code"] != 11110:
            self.root.get_screen("home").popup.content.ids.recipient.foreground_color = [255, 0, 0, 0.9]
            self.toast("Invalid recipient.")
            return

        idd = r["id"]

        if any(rec in d['text'] for d in self.root.get_screen("home").chats):
            self.root.get_screen("home").popup.content.ids.recipient.foreground_color = [255, 0, 0, 0.9]
            return self.toast("Already added.")

        Clock.schedule_once(partial(self.create_chat_2, rec, idd), 0)

    def create_chat_2(self, rec, idd, *_):
        self.set_current("home")
        self.root.get_screen("home").ids.first.opacity = 0
        self.root.get_screen("home").ids.first.height = 0
        Clock.schedule_once(partial(self.create_chat_3, rec, idd), 0)

    def create_chat_3(self, rec, idd, *_):
        avatar = self.session.post(self.api_url + "/user/avatar", json={"id": idd})

        r = self.session.post(self.api_url + "/user/user_create", json={"id": idd}).json()

        display_name = r["display_name"]
        public = r["public"]

        file_name = f'user_avatars/{idd}.png'

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{idd}.png"), 'wb') as f:
            f.write(avatar.content)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), 'r') as file:
            data = json.load(file)

        t = str(f"{datetime.now().strftime('%H:%M')}")

        message = rec
        about = "*No Bio Available*"

        data[encrypt(rec, self.unhashed_password)] = {
            "image": file_name,
            "message": encrypt(message, self.unhashed_password),
            "time": t,
            "about": encrypt(about, self.unhashed_password),
            "unread_messages": False,
            "user_id": idd,
            "public": str(public),
            "display": display_name
        }

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), 'w') as file:
            json.dump(data, file, indent=4)

        user_data = {
            "text": rec,
            "secondary_text": message,
            "time": t,
            "image": file_name,
            "unread_messages": False,
            "user_id": idd,
            "about": about,
            "public": str(public),
            "display": display_name
        }
        self.root.get_screen("home").chats.append(user_data)
        self.root.get_screen("home").original.append(user_data)

    def nah(self, touch, name):
        a, touch = touch
        if a.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                return
            self.is_touching = True
            self.long_press_trigger = Clock.schedule_once(partial(self.check_press_type, name),
                                                          0.1)

    def no(self, n, touch):
        if self.is_touching:
            if not n.collide_point(*touch.pos):
                self.cancel_press()

    def noo(self, n, touch, text):
        if self.is_touching:
            self.cancel_press()
            if n.collide_point(*touch.pos):
                self.current_chat_with = text
                self.start_chat(text)

    def check_press_type(self, name, *_):
        if self.is_touching:
            self.root.get_screen("home").user_settings(name)
            self.cancel_press()

    def cancel_press(self):
        self.is_touching = False
        if self.long_press_trigger:
            self.long_press_trigger.cancel()
            self.long_press_trigger = None

    def delete_user2(self, user):
        try:
            for item in self.root.get_screen("home").chats:
                if item["text"] == user:
                    self.root.get_screen("home").chats.remove(item)
                    self.root.get_screen("home").original.remove(item)
                    break

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), 'r') as file:
                data = json.load(file)

            for item in data:
                dec = decrypt(item, self.unhashed_password)
                if dec and dec == user:
                    data.pop(item)
                    break

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), 'w') as file:
                json.dump(data, file, indent=4)

            self.root.get_screen("contact_profile").popup2.dismiss(force=True)

            self.set_current("home")
            self.in_chat = False
            threading.Thread(target=self.close_chat_2).start()

            self.root.get_screen("home").ids.aaaa.refresh_from_data()

            if len(self.root.get_screen("home").original) == 0:
                Clock.schedule_once(self.hide_search, 0)

                self.root.get_screen("home").ids.first.opacity = 1
                self.root.get_screen("home").text_hidden = "1"

            self.root.get_screen("home").ids.aaaa.refresh_from_data()
        except:
            print(traceback.format_exc())
            pass

    @mainthread
    def hide_search(self, *_):
        self.root.get_screen("home").ids.field.text = ""
        self.root.get_screen("home").search_bar = True

    def signup(self, username, password, display_name):
        self.set_current("processing")
        threading.Thread(target=self.signup2, args=(username, password, display_name,)).start()

    def signup2(self, username, password, display_name):
        try:
            self.root.get_screen("processing").animate_text = "Processing"
            r = requests.post(self.api_url + "/user/exists", json={"username": username})
            if r.json()["exists"]:
                self.set_current("auth")
                self.toast("Username taken. Try again.")
                self.root.get_screen("auth").uname.shake()
                return

            self.root.get_screen("processing").animate_text = "Loading"

            if len(username) > 12:
                self.set_current("auth")
                self.root.get_screen("auth").uname.shake()
                self.toast("Username too long.")
                return

            self.root.get_screen("processing").animate_text = "Generating Keys"

            public, private = rsa.newkeys(2048)

            self.root.get_screen("processing").animate_text = "Setting everything up"

            r = self.session.post(self.api_url + "/register",
                                  json={"username": username, "password": password, "public": public.save_pkcs1().decode(), "device_token": self.device_token, "display_name": display_name})

            if r.json()["code"] == 11110:
                print(public, private)
                print("     [SUCCESS] Register successfull")
                set_public_key(username, password, public.save_pkcs1().decode())
                set_private_key(username, password, private.save_pkcs1().decode())

                self.login(username, password)
            elif r.json()["code"] == 10009:
                self.set_current("auth")
                self.toast("Username taken. Try again.")
                self.root.get_screen("auth").uname.shake()
                return
            else:
                self.set_current("auth")
                self.toast("Username taken. Try again.")
                self.root.get_screen("auth").uname.shake()
                return
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.set_current("auth")
            self.toast("Error signing in! Check connection.")

    def login(self, username, password):
        if not username:
            return self.root.get_screen("auth").uname.shake()
        if not password:
            return self.root.get_screen("auth").password.shake()
        self.set_current("processing")
        threading.Thread(target=self.login2, args=(username, password,)).start()

    @mainthread
    def set_current(self, s):
        self.root.set_current(s)

    def login2(self, username, password):
        try:
            if username == "" or password == "":
                return
            self.root.get_screen("processing").animate_text = "Logging in"
            r = self.session.post(self.api_url + "/login", json={"username": username, "password": password})
            if r.json()["code"] == 10003:
                self.username = username
                self.unhashed_password = password
                self.password = hash_pwd(password)

                self.set_current("2fa_verify")
            elif r.json()["code"] == 11110:
                if username != "Google":
                    public = get_public_key(username, password)
                    private = get_private_key(username, password)
                    print(public)
                    print(private)
                    if public and private:
                        self.public_key = rsa.PublicKey.load_pkcs1(public)
                        self.private_key = rsa.PrivateKey.load_pkcs1(private)
                        print(self.public_key)
                        print(self.private_key)
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

                self.avatar_path = "default.jpg" if not os.path.exists(
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 f"user_avatars/{idd}.png")) else os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{idd}.png")

                if platform != "android":  # For android, we use "my_foreground_callback"
                    threading.Thread(target=self.check_for_messages_on_home_screen).start()

                self.set_current("home")

                print(self.device_token)
            else:
                self.set_current("auth")
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
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            self.set_current("auth")
            self.toast("Error signing in! Check connection.")

    def send_message(self, text, uid):
        try:
            if not text:
                return

            print(self.public_key_of_partner)
            print(self.public_key)
            print(self.private_key)

            enc_identity = rsa.encrypt(f"{self.username}---{self.id}".encode(), self.public_key_of_partner)
            enc = rsa.encrypt(text.encode(), self.public_key_of_partner)
            signature = rsa.sign(text.encode(), self.private_key, "SHA-256")

            d = {
                "message": str(enc),
                "recipient": self.current_chat_with,
                "signature": str(signature),
                "identity": str(enc_identity),
            }

            d0 = {
                "message": str(enc),
                "recipient": self.current_chat_with,
                "signature": str(signature),
                "reply_to": self.mailbox
            }


            r0 = requests.post(self.api_url + "/v2/send", json=d0).json()
            print(r0)


            r = requests.post(self.api_url + "/send", json=d).json()

            if r["code"] != 11110:  # 11110
                delete_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)
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
        except:
            delete_dict_by_uid(self.root.get_screen("chat").chat_logs, uid)
            for item in self.root.get_screen("chat").ids.box.children:
                if item.uid == uid:
                    item.icon = "error_outline"
                    item.icon_color = "#fc050d"
                    break
            self.toast("Error sending message...")

    def change_avatar(self, *args):
        element = self.root.get_screen("user_settings").ids.profile_img
        if element.collide_point(*args[1].pos):
            if platform == "android":
                if not check_permission("android.permission.READ_MEDIA_IMAGES"):
                    return request_permissions([Permission.READ_MEDIA_IMAGES, Permission.READ_MEDIA_VIDEO])

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

        r = self.session.post(self.api_url + "/change/avatar", files={"upload_file": open(sel, "rb")})

        if r.json()["code"] == 11110:
            self.do_thing_with_selected(sel)
            return
        else:
            self.toast("Couldn't send file.")
            return

    @mainthread
    def do_thing_with_selected(self, sel):
        with open(sel, 'rb') as file:
            image_data = file.read()
        pp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"user_avatars/{self.id}.png")

        with open(pp, "wb") as file:
            file.write(image_data)

        shutil.copy(sel, pp)
        self.avatar_path = sel
        self.root.get_screen("user_settings").avatar_path = sel
        self.root.get_screen("user_settings").av(sel)

    def start_chat(self, user):
        self.set_current("chat")
        Clock.schedule_once(partial(self.start_chat_2, user), 0)

    def start_chat_2(self, user, *_):
        chat_screen = self.root.get_screen("chat")
        abs_usr = None
        for user_ in self.root.get_screen("home").chats:
            if str(user_["text"]) == str(user):
                abs_usr = user_
                break
        if not abs_usr:
            return toast("Error occurred.")

        public = rsa.PublicKey.load_pkcs1(abs_usr["public"])
        self.public_key_of_partner = public
        print(user)
        self.current_chat_with = user

        chat_screen.user = abs_usr
        chat_screen.image = abs_usr["image"]
        chat_screen.chat_logs = []
        chat_screen.title = abs_usr["text"]

        threading.Thread(target=self.do_thing_thread, args=(abs_usr["text"], public,)).start()

        r = requests.post(self.api_url + "/mailbox/open").json()
        print(r)
        self.mailbox = r["mailbox"]
        self.mailbox_key = r["key"]

        add_mailbox({"number": self.mailbox, "auth": self.mailbox_key})

    def do_thing_thread(self, rec, public):
        self._stop_event = threading.Event()
        self.message_thread = threading.Thread(target=self.receive_messages_private, args=(public,rec,))
        self.message_thread.start()

        for item in self.root.get_screen("home").ids.aaaa.data:
            if item["text"] == rec:
                item["unread_messages"] = False
                break

        self.root.get_screen("home").ids.aaaa.refresh_from_data()

        self.in_chat = True

        self.pause_thread2()

        for item in self.buffer_messages:
            print(item)
            if item["sender"].decode().split("---")[0] == rec:
                try:
                    rsa.verify(item["dec_message"], item["full_sign"], self.public_key_of_partner)
                except Exception as e:
                    self.open_warning(item["dec_message"])
                    print(e)
                    print("No verification")

                self.add_resp(item["dec_message"].decode())

                self.buffer_messages.remove(item)

    @mainthread
    def open_warning(self, mess):
        self.root.get_screen("chat").open_warning(mess=mess.decode())

    @staticmethod
    def save_base64_image(image_bytes, file_path):
        if not os.path.isdir("saved_data"):
            os.mkdir("saved_data")
        try:
            with open(file_path, "wb") as image_file:
                image_file.write(image_bytes)
            return True
        except Exception as _:
            return False

    @staticmethod
    def save_base64_file(image_bytes, file_path):
        if not os.path.isdir("saved_data"):
            os.mkdir("saved_data")
        try:
            with open(file_path, "wb") as image_file:
                image_file.write(image_bytes)
            return True
        except Exception as _:
            return False

    @mainthread
    def add_image(self, img):
        file_path = f"saved_data/{str(uuid.uuid4())}.png"
        self.save_base64_image(img, file_path)

        self.root.get_screen("chat").ids.box.add_widget(
            ImageMessage(source=file_path, send_by_user=False, file_size=self.get_image_size(file_path)))

    @mainthread
    def add_file(self, file, filename):
        file_path = f"saved_data/{str(uuid.uuid4())}{os.path.splitext(file)[1]}"
        self.save_base64_file(file, file_path)

        self.root.get_screen("chat").ids.box.add_widget(
            Attachment(source_=file_path, send_by_user=False, filename=filename, base="a", file_size=get_file_size(file_path)))

    def receive_messages_private(self, _, rec):
        print("     [DEBUG] (receive_messages_private) Started...")
        while not self._stop_event.is_set():
            try:
                res = self.session.post(self.api_url + "/receive")
                print(res.json())
                all_mailboxed = read_mailboxes()
                responses = []
                # for mailbox in all_mailboxed:
                #     r = requests.post(self.api_url + "/v2/receive", json={"mailbox": mailbox["number"], "key": mailbox["auth"]}).json()
                #     responses += r["messages"]

                responses += res.json()["messages"]
                print(responses)

                if res.json()["code"] == 11110:
                    for message in responses:
                        if not message.get("file"):
                            full_sign = eval(message["signature"])
                            sealed_sender = eval(message["identity"])
                            enc_message = eval(message["message"])

                            sender = rsa.decrypt(sealed_sender, self.private_key)
                            dec_message = rsa.decrypt(enc_message, self.private_key)

                            sender_username = sender.split(b"---")[0].decode()
                            print(sender_username)
                            print(rec)
                            print(self.current_chat_with)
                            if sender_username != rec:
                                self.buffer_messages.append(
                                    {"sender": sender, "dec_message": dec_message, "full_sign": full_sign})
                                return

                            try:
                                rsa.verify(dec_message, full_sign, self.public_key_of_partner)
                            except Exception as _:
                                self.open_warning(dec_message)

                            self.add_resp(dec_message.decode())
                        else:
                            if message["file_type"] == "image":
                                self.add_image(base64.b64decode(message["file"].encode()))
                            else:
                                self.add_file(base64.b64decode(message["file"].encode()), message["filename"])
            except Exception as e:
                print(e)
                print("Not established yet")
            time.sleep(2)
        print("     [DEBUG] (receive_messages_private) Stopped.")

    @mainthread
    def add_resp(self, text):
        self.root.get_screen("chat").ids.box.add_widget(
            ChatBubble2(text=extract_links(text), send_by_user=False, icon="check_circle"))

    def close_chat(self):
        self.set_current("home")
        self.in_chat = False
        threading.Thread(target=self.close_chat_2).start()

    def close_chat_2(self):
        try:
            self.stop_thread()
            self.message_thread.join()
        except:
            pass
        self.close_chat3()
        self.resume_thread2()

    @mainthread
    def close_chat3(self):
        try:
            self.root.get_screen("chat").ids.box.clear_widgets()
            self.root.get_screen("chat").chat_logs = []
        except:
            pass

    def nothing(self):
        pass

    def done_change(self):
        self.root.get_screen("settings").l.dismiss(force=True)

    @staticmethod
    def notify(title, message, icon_path=r"images\logo.png"):
        notification(
            title=title,
            message=message,
            app_icon=icon_path,
            timeout=30
        )

    def change_password(self, old, new):
        if old != self.unhashed_password:
            self.toast("Current Password is wrong.")
            return

        r = self.session.post(self.api_url + "/change/password", json={"new": new, "old": old})

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
        r = self.session.post(self.api_url + "/change/username", json={"new": uname})

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
        lang_to_id = config.lang_to_code(lang)
        if config.get_language() == lang_to_id:
            return
        config.set_language(lang_to_id)

        self.language = str(lang_to_id).upper()

    @staticmethod
    def translate(text):
        c = config.get_language()
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/translations.json')), "r") as file:
            j = json.load(file)
        try:
            t = j["translations"][str(c)][text]
            return t
        except:
            t = GoogleTranslator(source='en', target=c).translate(text=text)
            j["translations"][str(c)][text] = t
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/translations.json'),
                      "w") as file:
                json.dump(j, file, indent=4)
            return t

    def is_name_taken(self, name):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/users.json'), 'r') as file:
            data = json.load(file)
        return encrypt(name, self.unhashed_password) in data

    def block_user(self):
        # TODO: Implement
        return

    def enable_2fa(self):
        if self.has_2fa:
            # TODO: Implement
            self.set_current("disable_2fa")
        else:
            r = self.session.post(self.api_url + "/2fa/enable",
                                  json={"username": self.username, "password": self.unhashed_password})
            out = r.json()
            secret_key = out["secret_key"]
            rr = pyotp.totp.TOTP(secret_key).provisioning_uri(name=f'User {self.username}', issuer_name='Veilo')
            q = qrcode.make(rr)
            q.save("2fa_code.png")
            self.set_current("enable_2fa")
            self.set_token_2fa(secret_key)

    @mainthread
    def set_token_2fa(self, rr):
        self.root.get_screen("enable_2fa").token = rr

    def verify_2fa(self, code):  # TODO: Fix this (load pk from file)
        if self.has_2fa:
            return

        r = self.session.post(self.api_url + "/2fa/verify",
                              json={"username": self.username, "password": self.unhashed_password, "code": code})
        if r.json()["code"] != 11110:
            self.toast("Error verifying 2fa")
            self.set_current("auth")
            return

        self.has_2fa = True

        if self.username != "Google":
            with open(f"private_key.txt", "r") as file:
                a = file.read()
                dec_priv = a
                if dec_priv is None:
                    self.toast("Private key couldn't be decrypted.")
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

    @staticmethod
    def disable_2fa(_):
        return False

    def file_chooser(self):
        if platform == "android":
            if not check_permission("android.permission.READ_MEDIA_IMAGES"):
                return request_permissions([Permission.READ_MEDIA_IMAGES, Permission.READ_MEDIA_VIDEO])

        try:
            filechooser.open_file(on_selection=self.selected_file)
        except Exception as _:
            print(traceback.format_exc())
            pass

    @staticmethod
    def get_image_size(image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                return width, height
        except Exception:
            return None

    def send_file(self, file_path, image: bool = True):
        try:
            enc_identity = rsa.encrypt(f"{self.username}---{self.id}".encode(), self.public_key_of_partner)
            data = open(file_path, "rb").read()

            d = {
                "recipient": self.current_chat_with,
                "identity": str(enc_identity),
                "file_data": base64.b64encode(data).decode(),
                "type": "image" if image else "file"
            }

            if image:
                url = 'http://api.protdos.com/post_file'
                r = requests.post(url, json=d).json()

                if r["code"] != 11110:  # 11110
                    self.toast("Error sending image...")
            else:
                url = 'http://api.protdos.com/post_file'

                d["filename"] = os.path.basename(file_path)

                r = requests.post(url, json=d).json()

                if r["code"] != 11110:  # 11110
                    self.toast("Error sending file...")
        except Exception as _:
            self.toast("Error sending message...")
            print(traceback.format_exc())

    @mainthread
    def selected_file(self, selection):
        print(selection)
        # TODO: Implement multi-file sending
        try:
            if is_image_file(selection[0]):
                print("Is image.")
                self.send_file(selection[0], image=True)
                self.add_image_(selection[0])
            elif is_audio_file(selection[0]):
                self.root.get_screen("chat").ids.box.add_widget(AudioMessage(send_by_user=True))
            else:
                self.send_file(selection[0], image=False)
                self.root.get_screen("chat").ids.box.add_widget(
                    Attachment(send_by_user=True, filename=os.path.basename(selection[0]), pos_hint={"right": 1},
                               file_size=get_file_size(selection[0]), source_=selection[0]))
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            pass

    @mainthread
    def add_image_(self, selection):
        print(selection)
        self.root.get_screen("chat").ids.box.add_widget(
            ImageMessage(source=str(selection), send_by_user=True, pos_hint={"right": 1},
                         file_size=self.get_image_size(selection)))

    def on_stop(self):
        self._stop_event.set()
        self.is_running = False
        return False

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

    def open_link(self, _, link):
        self.root.get_screen("chat").open_link_warning(link)

    def dismiss(self):
        self.root.get_screen("chat").warn.dismiss(force=True)

    def dismiss2(self):
        self.root.get_screen("other").d.dismiss(force=True)

    def delete_account(self):
        self.set_current("auth")

        self.username = None
        self.password = None
        self.unhashed_password = None

        self.private_key = None
        self.public_key = None

        a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"assets/users.json"), "w")
        a.write("{}")
        a.close()

        script_path = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(script_path)

        for file_name in files:
            if "_key_" in file_name:
                file_path = os.path.join(script_path, file_name)
                os.remove(file_path)
                # print(f"Deleted: {file_path}")

        r = App.get_running_app().session.post(App.get_running_app().api_url + "/account/delete")

        self.is_running = False
        self.pause_event.set()

        return self.stop()

    def detect_breaches(self, email, phone):
        r = requests.post(self.api_url + "/breach", json={"email": email, "phone": phone})

        if r.json()["code"] == 11110:
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
        max_width = 350
        max_height = 350

        image = Image.open(file_path)

        original_width, original_height = image.size

        if original_width > max_width or original_height > max_height:
            ratio_width = max_width / original_width
            ratio_height = max_height / original_height
            resize_ratio = min(ratio_width, ratio_height)
            new_width = int(original_width * resize_ratio)
            new_height = int(original_height * resize_ratio)
        else:
            new_width = original_width
            new_height = original_height

        self.root.get_screen("chat").open_preview(file_path, size=(new_width, new_height))

    def download_file(self, path):
        path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))
        try:
            filename = os.path.basename(path)
            if platform == "android":
                full_path = os.path.join(primary_external_storage_path(), "DCIM", f"{str(uuid.uuid4())}_{filename}")
                Image.open(path).save(full_path)
                self.toast("Downloaded.")
                return
            Image.open(path).save(f"{str(uuid.uuid4())}_{filename}")
            self.toast("Downloaded.")
        except:
            print("Not an image.")
            # TODO: Do this for not-image too

    def check_pull_refresh(self, view, _):
        if self.is_still_up:
            if view.scroll_y > 0.7:
                self.is_still_up = False

        if view.scroll_y < 0.7:
            if not self.refreshing:
                self.is_still_up = True

    def check_pull_refresh_down(self, *_):
        if not self.refreshing:
            if self.is_still_up:
                if self.root.get_screen("home").text_hidden != "1":
                    self.refreshing = True
                    threading.Thread(target=self.update_data).start()

    def update_data(self):
        ps = self.unhashed_password

        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)),
                                            'assets/users.json')), 'r') as f:
            data = json.load(f)

        chats = []

        if data != {}:
            for i in data:
                i_dec = decrypt(i, ps)
                if i_dec is not None:
                    user_data = {
                        "text": i_dec,
                        "secondary_text": decrypt(data[i]["message"], ps),
                        "time": data[i]["time"],
                        "image": data[i]["image"],
                        "name": i,
                        "unread_messages": data[i]["unread_messages"],
                        "user_id": data[i]["user_id"]
                    }
                    chats.append(user_data)
            if len(chats) == 0:
                self.set_hide_show(1)
        else:
            self.set_hide_show(1)

        for item in chats:
            img_path = item["image"]
            img_hash = hashlib.sha256(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), img_path.split("/")[0], img_path.split("/")[1]), "rb").read()).hexdigest()

            r = requests.post(self.api_url + "/user/avatar/hash_verify", json={"id": item["user_id"], "hash": img_hash})
            try:
                _ = r.json()
            except:
                file_name = f'user_avatars/{item["user_id"]}.png'
                item["image"] = f'user_avatars/{item["user_id"]}.png'
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name.split("/")[0], file_name.split("/")[1]), "wb") as f:
                    f.write(r.content)

        self.set_refreshing_false()  # Has to be in @mainthread

    @mainthread
    def set_refreshing_false(self):
        self.root.get_screen("home").ids.first.opacity = 0
        self.root.get_screen("home").text_hidden = "0"

        self.root.get_screen("home").ids.aaaa.refresh_from_data()

        old_paths = []

        for item in self.root.get_screen("home").chats:
            old_path = item["image"]
            item["image"] = "user_avatars/Default/default.png"
            old_paths.append(old_path)

        self.root.get_screen("home").ids.aaaa.refresh_from_data()

        self.set_refreshing_false2(old_paths)

    @mainthread
    def set_refreshing_false2(self, old_paths):
        for i, item in enumerate(old_paths):
            self.root.get_screen("home").chats[i]["image"] = item

        self.root.get_screen("home").ids.aaaa.refresh_from_data()

        self.refreshing = False

    def refresh_data(self):
        self.refreshing = True
        threading.Thread(target=self._refresh_data).start()

    @mainthread
    def cll(self):
        self.root.get_screen("home").ids.grid.clear_widgets()
        self.root.get_screen("home").chats = []

    @mainthread
    def set_hide_show(self, val):
        self.root.get_screen("home").ids.first.opacity = int(val)
        self.root.get_screen("home").text_hidden = str(val)

    def _refresh_data(self):
        self.root.get_screen("home").ids.first.opacity = 1
        self.root.get_screen("home").text_hidden = "1"

    def _refresh_data_old(self):
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

        for item in chats:
            try:
                name = item["text"]
                idd = requests.post(self.api_url + "/user/id", json={"recipient": name}).json()["id"]
                r = requests.post(self.api_url + "/user/avatar", json={"id": idd})
                file_name = f'user_avatars/{idd}.png'
                item["image"] = f'user_avatars/{idd}.png'
                with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)), "wb") as f:
                    f.write(r.content)
            except:
                pass

        self.add_data()

        d = {}
        for item in chats:
            d[item["name"]] = {
                "image": item["image"],
                "message": item["message"],
                "time": item["time"],
                "about": item["about"],
                "unread_messages": False,
                "user_id": item["user_id"]
            }

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "users.json"), "w") as file:
            json.dump(d, file, indent=4)

        self.cll()

        data = d

        if data != {}:
            for i in data:
                i_dec = decrypt(i, ps)
                if i_dec is not None:
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

    def change_bio(self, bio_text):
        r = self.session.post(self.api_url + "/change/biography", json={"new": bio_text}).json()
        if r["code"] == 11110:
            return toast("Successfully changed bio.")
        return toast("Error occurred.")

    def show_searchbar(self):
        threading.Thread(target=self.root.get_screen("home").load_all).start()
        if self.root.get_screen("home").search_bar:
            self.root.get_screen("home").search_bar = False
            self.root.get_screen("home").ids.field.text = ""
        else:
            self.root.get_screen("home").search_bar = True

    def show_searchbar2(self):
        if not self.root.get_screen("home").original:
            return
        if self.root.get_screen("home").search_bar:
            self.root.get_screen("home").search_bar = False
            self.root.get_screen("home").ids.field.text = ""
        else:
            self.root.get_screen("home").search_bar = True
        self.root.get_screen("home").chats = self.root.get_screen("home").original

    def create_group(self, group_name):
        if group_name:
            self.root.get_screen("home").popup.dismiss(force=True)
            self.root.set_current("group_members")
            return
        self.toast("Please enter a group name.")

    def select(self, *args):
        self.root.get_screen("group_members").check_click(*args)


if __name__ == "__main__":
    VeiloApp().run()
