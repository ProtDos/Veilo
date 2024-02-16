from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Animation
from kivy.properties import ColorProperty, StringProperty
from components.screen import PScreen
from components.boxlayout import PBoxLayout
from kivy.utils import rgba


class DisplayName(PScreen):
    bg_color = ColorProperty()
    username = StringProperty()
    password = StringProperty()
    btn_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.btn_color = rgba(50, 44, 106, 255)

    def get_started(self):
        if not self.ids.uname.text:
            return self.ids.uname.shake()

        # print("asd")

        # Animation(d=0.4, pos_hint={"center_y": 0.5}).start(self.ids.get_btn)

        # print("2")
#
        # Animation(btn_color=self.theme_cls.primary_color, d=0.4).start(self)
#
        # self.ids.get_btn.text = ""
#
        # print("asdasd")
#
        # Animation(
        #     d=0.7, size_hint=(1.2, 1.2)
        # ).start(self.ids.get_btn)
#
        # print("here")

        self.do_it()

    def do_it(self):
        App.get_running_app().signup(self.username, self.password, self.ids.uname.text)
