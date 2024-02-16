import requests
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ColorProperty
from components.screen import PScreen
from components.toast import toast
from kivy.utils import rgba, get_color_from_hex, platform
from utils.configparser import config
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from password_strength import PasswordPolicy

if platform == "android":
    from android.permissions import request_permissions, Permission


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
    return password_strength.strength() * 100


class AuthScreen(PScreen):
    bg_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.primary_color

        self.ids.password.bind(text=self.on_text)

        a = config.is_startup()

        if platform == "android":
            Clock.schedule_once(self.show_form, 0)
        else:
            if a == "True" or a is True:
                Clock.schedule_once(self.show_form, 5)
            else:
                Clock.schedule_once(self.show_form, 3)


    def on_text(self, _, value):
        if value:
            x = calculate_password_strength(value)
            if x <= 20:
                self.ids.password.foreground_color = [255, 0, 0, 0.9]
            elif x <= 70:
                self.ids.password.foreground_color = get_color_from_hex("#ffd700d9")
            else:
                self.ids.password.foreground_color = [0, 255, 0, 0.9]

    def show_form(self, *_):
        if platform == "android":
            request_permissions([Permission.POST_NOTIFICATIONS])

        Animation(bg_color=self.theme_cls.bg_normal, d=0.4).start(self)

        Animation(
            d=0.7, scale=0.75, text_color=self.theme_cls.primary_color
        ).start(self.ids.title)

        Animation(d=0.7, pos_hint={"center_y": 0.75}).start(self.ids.intro)

        self.ids.form.disabled = False

        a = config.is_startup()


        if a == "True" or a is True:
            PDialog(content=AboutDialogContent2()).open()

    def sign_in(self):
        self.manager.set_current("home")
        toast("Signed In successfully!")


    def signup(self, username, password):
        if not username:
            return self.ids.uname.shake()
        if not password:
            return self.ids.password.shake()

        r = requests.post(App.get_running_app().api_url + "/user/exists", json={"username": username})
        if r.json()["exists"]:
            toast("Username taken.")
            self.ids.uname.shake()
            return

        App.get_running_app().root.set_current("display_name")
        self.manager.get_screen("display_name").username = username
        self.manager.get_screen("display_name").password = password


    def show_password(self):
        if self.ids.password.password:
            self.ids.password.password = False
            self.ids.btn.icon = "eye_off"
        else:
            self.ids.password.password = True
            self.ids.btn.icon = "eye"


class AboutDialogContent2(PBoxLayout):
    pass
