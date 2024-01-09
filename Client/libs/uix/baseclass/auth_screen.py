from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ColorProperty

from components.screen import PScreen
from components.toast import toast

from utils.configparser import config

from components.boxlayout import PBoxLayout
from components.dialog import PDialog


from password_strength import PasswordPolicy


def calculate_password_strength(password):
    # Define the password policy with desired constraints
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


class AuthScreen(PScreen):
    bg_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.primary_color

        self.ids.password.bind(text=self.on_text)

        a = config.is_startup()

        if a == "True" or a is True:
            Clock.schedule_once(self.show_form, 5)
        else:
            Clock.schedule_once(self.show_form, 3)


    def on_text(self, instance, value):
        if value:
            x = calculate_password_strength(value)
            print(x)
            if x <= 20:
                self.ids.password.foreground_color = [255, 0, 0, 0.9]
            elif x <= 70:
                self.ids.password.foreground_color = [255, 215, 0, 0.85]
            else:
                self.ids.password.foreground_color = [0, 255, 0, 0.9]

    def show_form(self, *args):

        # self.ids.intro.remove_widget(self.ids.intro_btn)
        Animation(bg_color=self.theme_cls.bg_normal, d=0.4).start(self)

        Animation(
            d=0.7, scale=0.75, text_color=self.theme_cls.primary_color
        ).start(self.ids.title)

        Animation(d=0.7, pos_hint={"center_y": 0.75}).start(self.ids.intro)

        self.ids.form.disabled = False
        self.ids.btn_1.disabled = False
        self.ids.btn_2.disabled = False

        a = config.is_startup()

        self.ids.btn.y = self.ids.password.y - 2

        if a == "True" or a is True:
            PDialog(content=AboutDialogContent2()).open()

    def sign_in(self):
        self.manager.set_current("home")
        toast("Signed In successfully!")

    def sign_up(self):
        self.ids.uname.shake()
        toast("Account created successfully! Please Sign In to jump in!")

    def show_password(self):
        if self.ids.password.password:
            self.ids.password.password = False
            self.ids.btn.icon = "eye_off"
        else:
            self.ids.password.password = True
            self.ids.btn.icon = "eye"


class AboutDialogContent2(PBoxLayout):
    pass
