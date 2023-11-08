import json
import threading
import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import sp
from kivy.properties import ListProperty, NumericProperty, StringProperty
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

    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.load_all, 0)

    def load_all(self, dt):
        ps = App.get_running_app().unhashed_password

        with open("assets/users.json") as f:
            self.data = json.load(f)

        print(len(self.data))

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

        print("-"*10)
        print(self.chats)
        print(len(self.data))
        print()
        print(self.data)
        print("-" * 10)

    def goto_chat_screen(self, user3):
        try:
            ps = App.get_running_app().unhashed_password
            print("-"*50)
            print(ps)
            print(user3)
            with open("assets/users.json") as f:
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
        with open("assets/users.json") as f:
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
    def switch(self):
        if self.ids.i_btn.icon == "account_group":
            self.ids.i_btn.icon = "people_outline"
            self.ids.lbl_1.text = "Create a new group by entering a unique name"
            self.ids.recipient.original = "Group name"
            # self.ids.create.on_release = self.custom_release
        else:
            self.ids.i_btn.icon = "account_group"
            self.ids.lbl_1.text = "Enter in your recipient to start a new chat."
            self.ids.recipient.original = "Recipient"

    def custom_release(self, text):
        if self.ids.i_btn.icon == "account_group":
            App.get_running_app().create_chat(text)
        else:
            print(f"Creating group: {text}")


class UserInfoDialogContent(PBoxLayout):
    title = StringProperty()
    image = StringProperty()
    about = StringProperty()


