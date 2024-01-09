import os.path
import re
import uuid
import wavio
import numpy as np
import sounddevice as sd
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import DictProperty, ListProperty, StringProperty

from components.dialog import PDialog
from components.screen import PScreen
from core.encryption import encrypt, decrypt
from components.boxlayout import PBoxLayout
from components.chat_bubble import AudioMessage, ChatBubble2


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


def is_malicious_file(filename):
    malicious_extensions = ['.exe', '.dll', '.bat', '.vbs', '.js', '.ps1', '.jar', '.py', '.scr']

    # Get the file extension from the filename
    file_extension = filename.split('.')[-1].lower()

    if file_extension in malicious_extensions:
        return True
    else:
        return False


def split_text(text, max_length=10):
    parts = []
    current_part = ""
    words = re.findall(r'\S+\s*', text)

    for word in words:
        if len(current_part) + len(word) <= max_length:
            current_part += word
        else:
            parts.append(current_part.strip())
            current_part = word
        if len(current_part) > max_length:
            # Handle cases where a single word is longer than max_length
            while len(current_part) > max_length:
                parts.append(current_part[:max_length])
                current_part = current_part[max_length:]

    if current_part:
        parts.append(current_part.strip())

    return parts


class ChatScreen(PScreen):
    user = DictProperty()
    title = StringProperty()
    chat_logs = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.field.bind(text=self.on_text)

        self.recorded_data = []  # To store the recorded audio data

        self.is_running = False

    def on_text(self, instance, value):
        if value:
            self.ids.send_mic_btn.icon = "send_lock"

            # self.ids.send_mic_btn.on_touch_down = None
            # self.ids.send_mic_btn.on_touch_up = None

            self.ids.send_mic_btn.bind(on_release=self.send)
            self.ids.send_mic_btn.bind(on_touch_down=self.nothing)
            self.ids.send_mic_btn.bind(on_touch_up=self.nothing)

            # self.ids.send_mic_btn.on_release = self.send(self.ids.field.text.strip())
            # self.ids.send_mic_btn.on_release = partial(self.send, self.ids.field.text.strip())

        else:
            self.ids.send_mic_btn.icon = "microphone"

            # self.ids.send_mic_btn.on_touch_down = self.stop_recording
            # self.ids.send_mic_btn.on_touch_up = self.stop_recording
#
            # self.ids.send_mic_btn.on_release = None

            self.ids.send_mic_btn.bind(on_release=self.nothing)
            self.ids.send_mic_btn.bind(on_touch_down=self.start_recording)
            self.ids.send_mic_btn.bind(on_touch_up=self.stop_recording)

    def nothing(self, *args):
        pass

    def start_recording(self, instance, touch):
        if self.ids.send_mic_btn.icon == "microphone":
            if self.ids.send_mic_btn.collide_point(*touch.pos):
                if not self.is_running:
                    print("Started")
                    self.recorded_data = []
                    self.recording_stream = sd.InputStream(channels=2, callback=self.audio_callback)
                    self.recording_stream.start()
                    self.is_running = True

    def stop_recording(self, instance, touch):
        if self.ids.send_mic_btn.icon == "microphone":
            if self.ids.send_mic_btn.collide_point(*touch.pos):
                if self.recording_stream:
                    print(self.is_running)
                    if self.is_running:
                        print("Stopped.")
                        self.is_running = False
                        self.recording_stream.stop()
                        self.recording_stream.close()
                        self.save_audio_to_file()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.recorded_data.append(indata.copy())

    def save_audio_to_file(self):
        if self.recorded_data:
            audio_data = np.concatenate(self.recorded_data, axis=0)
            if not os.path.isdir("temp_audio"):
                os.mkdir("temp_audio")
            filename = os.path.join("temp_audio", f"{str(uuid.uuid4())}.wav")
            wavio.write(filename, audio_data, 44100, sampwidth=3)

            self.ids.box.add_widget(AudioMessage(send_by_user=True, filename_data=filename))


    def open_preview(self, path, size):
        self.p = PDialog(
            content=Preview(
                source_=path,
                size_=size
            )
        )
        self.p.open()

    def add_message(self, text, side, color):
        # create a message for the recycleview
        self.chat_logs.append({
            'message_id': len(self.chat_logs),
            'text': text,
            'side': side,
            'bg_color': color,
            'text_size': [None, None],
        })

    def answer(self, text, *args):
        self.add_message('do you really think so?', 'left', '#332211')

    def send(self, *args):
        text = self.ids.field.text.strip()
        print(text)
        if not text:
            return

        ##############################
        # self.add_message(text, 'right', '#223344')
        # Clock.schedule_once(lambda *args: self.answer(text), 1)
        # self.answer(text)

        ##############################

        uid = str(uuid.uuid4())
        # self.chat_logs.append(
        #     {"text": extract_links(text), "send_by_user": True, "pos_hint": {"right": 1}, "idd": uid, "icon": "clock"}
        # )
        self.ids.box.add_widget(ChatBubble2(text=extract_links(text), send_by_user=True, pos_hint={"right": 1}, icon="clock", uid=uid))

        self.scroll_to_bottom()
        self.ids.field.text = ""
        # self.ids.chat_rv.viewclass = "AudioMessage"
        Clock.schedule_once(partial(self.later, str(text), uid), 1)

    def later(self, text, uid, *args):
        App.get_running_app().send_message(text, uid=uid)

    def receive(self, text):
        self.chat_logs.append(
            {
                "text": text,
                "send_by_user": False,
            }
        )

    def show_user_info(self):
        ps = App.get_running_app().unhashed_password
        # PDialog(
        #     content=UserInfoDialogContent(
        #         title=self.user["name"],
        #         image=self.user["image"],
        #         about=self.user["about"],
        #     )
        # ).open()

        self.manager.set_current("contact_profile")

        self.manager.get_screen("contact_profile").title = self.user["name"]
        self.manager.get_screen("contact_profile").image = self.user["image"]
        self.manager.get_screen("contact_profile").about = decrypt(self.user["about"], ps)

    def scroll_to_bottom(self):
        rv = self.ids.chat_rv
        box = self.ids.box
        if rv.height < box.height:
            Animation.cancel_all(rv, "scroll_y")
            Animation(scroll_y=0, t="out_quad", d=0.5).start(rv)

    def open_warning(self, mess):
        PDialog(
            content=VerifyFail(
                message=mess
            )
        ).open()

    def open_link_warning(self, link):
        self.warn = PDialog(content=LinkVerify(message=link))
        self.warn.open()


class UserInfoDialogContent(PBoxLayout):
    title = StringProperty()
    image = StringProperty()
    about = StringProperty()


class VerifyFail(PBoxLayout):
    message = StringProperty()


class LinkVerify(PBoxLayout):
    message = StringProperty()


class Preview(ButtonBehavior, PBoxLayout):
    source_ = StringProperty()
    size_ = ListProperty()
