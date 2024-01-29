import webbrowser

from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from utils.configparser import config
from password_strength import PasswordPolicy

from kivy.app import App


def calculate_password_strength(password):
    policy = PasswordPolicy.from_names(
        length=8,  # Minimum password length
        uppercase=1,  # Require at least one uppercase letter
        numbers=1,  # Require at least one number
        special=1,  # Require at least one special character
        nonletters=1,  # Require at least one non-letter character (e.g., digits or special characters)
    )

    # Check password against the defined policy and get the score
    password_strength = policy.password(password)

    print(password_strength.strength())

    return password_strength.strength() * 100


class UserSettings(PScreen):
    avatar_path = StringProperty(App.get_running_app().avatar_path)
    unasme = StringProperty(App.get_running_app().username)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def av(self, path):
        self.avatar_path = path
        print("lolo: ", self.avatar_path)

    def change_password(self):
        self.d = PDialog(content=PasswordChange())
        self.d.open()

    def change_username(self):
        self.d2 = PDialog(content=UsernameChange())
        self.d2.open()

    def change_abt(self):
        self.d3 = PDialog(content=BioChange())
        self.d3.open()

    def breach(self):
        self.b = PDialog(content=BreachDialog())
        self.b.open()

    def get_usrname(self):
        return App.get_running_app().username


class AboutDialogContent(PBoxLayout):
    pass


class BioChange(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PasswordChange(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.new.bind(text=self.on_text)

    def on_text(self, _, value):
        if value:
            x = calculate_password_strength(value)
            print(x)
            if x <= 20:
                self.ids.new.foreground_color = [255, 0, 0, 0.9]
            elif x <= 70:
                self.ids.new.foreground_color = [255, 215, 0, 0.85]
            else:
                self.ids.new.foreground_color = [0, 255, 0, 0.9]


class UsernameChange(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BreachDialog(PBoxLayout):
    def submit(self, email, phone):
        if email == "" and phone == "":
            return

    def a(self, *args):
        if self.ids.okay.collide_point(*args[1].pos):
            webbrowser.open("https://veilo.protdos.com/breaches_help")
