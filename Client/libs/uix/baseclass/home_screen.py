import json
import os
import threading
import time

import rsa
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import sp
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.button import Button
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.label import PLabel
from kivy.app import App
from components.toast import toast


from core.encryption import encrypt, decrypt


class HomeScreen(PScreen):

    chats = ListProperty()

    popup = None
    popup2 = None

    text_hidden = StringProperty("0")
    search_bar = BooleanProperty(True)

    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.load_all, 0)

        self.original = None

        self.ids.field.bind(text=self.on_text)

    def on_text(self, instance, value):
        if value:
            for item in self.original:
                if value not in item["text"]:
                    try:
                        self.chats.remove(item)
                    except:
                        pass
                else:
                    if item not in self.chats:
                        self.chats.append(item)
        else:
            self.chats = self.original

    def show_original(self, *args):
        print("-"*20)
        print(self.chats)
        print(self.original)
        self.chats = [i for i in self.original]


        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)), 'assets/users.json')), 'r') as f:
            self.data = json.load(f)

        print(self.data)

        print("-" * 20)

    def load_all(self, *args):
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
                    }
                    self.chats.append(user_data)
            print(self.chats)
            if len(self.chats) == 0:
                self.ids.first.opacity = 1
                self.text_hidden = "1"
        else:
            self.ids.first.opacity = 1
            self.text_hidden = "1"

        self.original = tuple(self.chats)

        print("-"*30)
        print("Original:", self.original)
        print("Chats:", self.chats)
        print("Data:", self.data)
        print("-" * 30)


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
            print("-"*50)
            print(ps)
            print(user3)
            with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(App.get_running_app().my_file_path)),
                                                'assets/users.json'))) as f:
                self.data = json.load(f)
            print(self.data)
            print("-" * 50)
            for item in self.data:
                if decrypt(item, ps) == user3:
                    user = {
                         "name": user3,
                         **self.data[item],
                    }
                    break

            self.manager.set_current("chat")
            chat_screen = self.manager.get_screen("chat")
            chat_screen.user = user
            chat_screen.chat_logs = []
            chat_screen.title = user["name"]
            # chat_screen.receive(user["message"])
        except UnboundLocalError:
            toast("Error")
        except Exception as e:
            print(e)

    def show_menu(self, *args):
        PDialog(content=MenuDialogContent()).open()

    def create(self):
        self.popup = PDialog(content=CreatePopup())
        self.popup.open()

    def user_settings(self, name):
        #  with open("assets/users.json") as f:
        #      data = json.load(f)
        #  try:
        #      self.ids.popup2.dismiss(force=True)
        #  except:
        #      pass
        #  for item in data:
        #      if item == name:
        #          print(item)
        #          print(data[item])
        #          self.popup2 = PDialog(
        #              content=UserInfoDialogContent(
        #                  title=item,
        #                  image=data[item]["image"],
        #                  about=data[item]["about"],
        #              )
        #          )
        #          self.popup2.open()
        #          return
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
        threading.Thread(target=self.animate_plus).start()

    def animate_plus(self):
        print("Here")
        for i in range(20):
            self.angle += 9
            time.sleep(.01)


class MenuDialogContent(PBoxLayout):
    pass


class CreatePopup(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.recipient.bind(text=self.on_text)

    def on_text(self, *args):
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


