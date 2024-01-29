import json
import os
import threading
import time
import traceback

import rsa
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from kivy.app import App
from components.toast import toast
from core.encryption import encrypt, decrypt


class HomeScreen(PScreen):

    chats = ListProperty()
    original = ListProperty()

    popup = None
    popup2 = None

    text_hidden = StringProperty("0")
    search_bar = BooleanProperty(True)

    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.load_all, 0)

        self.ids.field.bind(text=self.on_text)
        self.current_animation = None

    def on_text(self, _, value):
        if value:
            for item in self.original:
                if value.lower() not in item["text"].lower():
                    try:
                        self.chats.remove(item)
                    except:
                        pass
                else:
                    if item not in self.chats:
                        self.chats.append(item)
        else:
            self.chats = self.original

    def show_original(self, *_):
        self.chats = [i for i in self.original]
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)), 'assets/users.json')), 'r') as f:
            self.data = json.load(f)

    def load_all(self, *_):
        ps = App.get_running_app().unhashed_password

        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)), 'assets/users.json')), 'r') as f:
            self.data = json.load(f)

        self.chats = []

        if self.data != {}:
            for i in self.data:
                i_dec = decrypt(i, ps)
                if i_dec is not None:
                    user_data = {
                        "text": i_dec,
                        "secondary_text": decrypt(self.data[i]["message"], ps),
                        "time": self.data[i]["time"],
                        "image": self.data[i]["image"],
                        "name": i,
                        "unread_messages": self.data[i]["unread_messages"],
                        "about": decrypt(self.data[i]["about"], ps),
                        "public": self.data[i]["public"]
                    }
                    self.chats.append(user_data)
            if len(self.chats) == 0:
                self.ids.first.opacity = 1
                self.text_hidden = "1"
        else:
            self.ids.first.opacity = 1
            self.text_hidden = "1"

        for item in self.chats:
            self.original.append(item)


    def goto_chat_screen(self, user3):
        try:
            print("GOING TO USER:", user3)
            for item in App.get_running_app().buffer_messages:
                try:
                    rsa.verify(item["dec_message"], item["full_sign"], App.get_running_app().public_key_of_partner)
                except Exception as e:
                    App.get_running_app().open_warning(item["dec_message"])
                    print(e)
                    print("No verification")

                App.get_running_app().add_resp(item["dec_message"].decode())

                App.get_running_app().buffer_messages.remove(item)

            ps = App.get_running_app().unhashed_password
            with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)),
                                                'assets/users.json'))) as f:
                self.data = json.load(f)
            for item in self.data:
                if decrypt(item, ps) == user3:
                    user = {
                         "name": user3,
                         **self.data[item],
                    }
                    break

            try:
                _ = user
            except:
                return toast("Error!")

            self.manager.set_current("chat")
            App.get_running_app().root.set_current("chat")
            chat_screen = self.manager.get_screen("chat")
            chat_screen.user = user
            chat_screen.image = user["image"]
            chat_screen.chat_logs = []
            chat_screen.title = user["name"]
        except Exception as e:
            print(e)
            print(traceback.format_exc())


    def show_menu(self, *_):
        PDialog(content=MenuDialogContent()).open()

    def create(self):
        self.popup = PDialog(content=CreatePopup())
        self.popup.open()

    def user_settings(self, name):
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)), 'assets/users.json'))) as f:
            data = json.load(f)
        ps = App.get_running_app().unhashed_password
        for item in data:
            if decrypt(item, ps) == name:
                print(item)
                print(data[item])

                self.manager.set_current("contact_profile")

                self.manager.get_screen("contact_profile").title = decrypt(item, ps)
                self.manager.get_screen("contact_profile").image = data[item]["image"]
                self.manager.get_screen("contact_profile").about = decrypt(data[item]["about"], ps)

    def ann(self):
        self.current_animation = Animation(angle=180, duration=0.15)
        self.current_animation.bind(on_complete=self.stop_it)
        self.current_animation.start(self)

    def stop_it(self, anim, widget):
        anim.cancel(widget)
        anim.stop(widget)
        Animation.stop_all(widget)
        self.current_animation = None
        widget.angle = 0


class MenuDialogContent(PBoxLayout):
    pass


class CreatePopup(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.recipient.bind(text=self.on_text)

    def on_text(self, *_):
        self.ids.recipient.foreground_color = [0.5, 0.5, 0.5, 0.5]

    def switch(self):
        if self.ids.i_btn.icon == "account_group":
            self.ids.i_btn.icon = "people_outline"
            self.ids.lbl_1.text = "Create a new group by entering a name."
            self.ids.recipient.hint_text = "Group name"
            self.ids.big_label.text = "Group"
        else:
            self.ids.i_btn.icon = "account_group"
            self.ids.lbl_1.text = "Enter in your recipient to start a new chat."
            self.ids.recipient.hint_text = "Recipient"
            self.ids.big_label.text = "Chat"

    def custom_release(self, text):
        if self.ids.i_btn.icon == "account_group":
            App.get_running_app().create_chat(text)
        else:
            print(f"Creating group: {text}")
            App.get_running_app().create_group(text)


class UserInfoDialogContent(PBoxLayout):
    title = StringProperty()
    image = StringProperty()
    about = StringProperty()
