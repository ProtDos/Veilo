from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.properties import ColorProperty, OptionProperty
from kivy.utils import get_color_from_hex as gch

from core import font_definitions
from utils.configparser import config

# INFO: better color: #6B6F72


class ThemeManager(EventDispatcher):
    primary_color = ColorProperty(config.get_main_color())  # ColorProperty("684bbf")

    primary_light = ColorProperty(config.get_sec_color())  # ColorProperty("9b78f2")

    primary_dark = ColorProperty(config.get_main_color())  # ColorProperty("34218e")

    bg_normal = ColorProperty()

    bg_light = ColorProperty()

    bg_dark = ColorProperty()

    text_color = ColorProperty()

    theme_style = OptionProperty("Light", options=["Light", "Dark"])

    def on_theme_style(self, _, value):
        Window.clearcolor = gch("ffffff" if value == "Light" else "121212")  # FAFAFA
        if value == "Light":
            self.text_color = "000000"
            self.bg_light = "ffffff"
            self.bg_dark = "c7c7c7"
            self.bg_normal = "ffffff"  # FAFAFA
        else:
            self.text_color = "FFFFFF"
            self.bg_light = "383838"
            self.bg_dark = "000000"
            self.bg_normal = "121212"

    def update(self, color, light):
        self.primary_color = color
        self.primary_light = light
        self.primary_dark = color

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        font_definitions.register_fonts()
        Clock.schedule_once(
            lambda x: self.on_theme_style(None, self.theme_style)
        )


class ThemableBehavior(EventDispatcher):
    def __init__(self, **kwargs):
        self.theme_cls = App.get_running_app().theme_cls
        super().__init__(**kwargs)
