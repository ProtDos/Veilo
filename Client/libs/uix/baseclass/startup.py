from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ColorProperty

from components.screen import PScreen
from components.toast import toast

from utils.configparser import config

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from kivy.utils import get_color_from_hex as gch, rgba


class Startup(PScreen):
    bg_color = ColorProperty()
    btn_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = gch("FFFFFF")

        self.btn_color = rgba(50, 44, 106, 255)

        self.bg_color = self.theme_cls.primary_color

        Clock.schedule_once(self.show_form, 5)

    def show_form(self, _):
        Animation(bg_color=gch("FFFFFF"), d=0.4).start(self)

        Animation(
            d=0.7, scale=0, text_color=self.theme_cls.primary_color
        ).start(self.ids.title)

        Animation(d=0.7, pos_hint={"center_y": 0.75}).start(self.ids.intro)

        self.ids.layy.disabled = False
        self.ids.slide0.disabled = False
        self.ids.slide1.disabled = False
        self.ids.slide2.disabled = False

        self.bg_color = gch("FFFFFF")

    def current_slide(self, index):
        if index == 2:
            Animation(d=0.2, pos_hint={"center_y": 0.17}).start(self.ids.slide0)
            Animation(d=0.2, pos_hint={"center_y": 0.17}).start(self.ids.slide1)
            Animation(d=0.2, pos_hint={"center_y": 0.17}).start(self.ids.slide2)
        else:
            Animation(d=0.2, pos_hint={"center_y": 0.1}).start(self.ids.slide0)
            Animation(d=0.2, pos_hint={"center_y": 0.1}).start(self.ids.slide1)
            Animation(d=0.2, pos_hint={"center_y": 0.1}).start(self.ids.slide2)

        for i in range(3):
            if index == i:
                self.ids[f"slide{index}"].text_color = rgba(253, 140, 95, 255)
            else:
                self.ids[f"slide{i}"].text_color = rgba(233, 237, 250, 255)

    def next(self):
        self.ids.carousel.load_next(mode="next")

    def before(self):
        self.ids.carousel.load_previous()

    def end(self):
        self.ids.carousel.index = 2

    def get_started(self):
        self.ids.slide0.disabled = True
        self.ids.slide1.disabled = True
        self.ids.slide2.disabled = True

        Animation(d=0.4, pos_hint={"center_y": 0.5}).start(self.ids.get_btn)

        Animation(btn_color=self.theme_cls.primary_color, d=0.4).start(self)

        self.ids.get_btn.text = ""

        Animation(
            d=0.7, size_hint=(1.2, 1.2)
        ).start(self.ids.get_btn)

        Clock.schedule_once(self.redirect, 0.8)

    def redirect(self, dt):
        self.manager.set_current("auth", quick=True)


class AboutDialogContent2(PBoxLayout):
    pass


class LongItem(PBoxLayout):
    pass
