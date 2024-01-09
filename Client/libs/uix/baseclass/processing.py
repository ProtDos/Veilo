import json

import requests
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ColorProperty, BooleanProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from kivy.uix.floatlayout import FloatLayout
from utils.configparser import config
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as gch


class Processing(PScreen):
    animate_text = StringProperty("Processing")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = gch("#ffffff")
        Clock.schedule_interval(self.update, .6)

    def update(self, dt):
        try:
            self.animate_text += "." if not "..." in self.animate_text else self.clear()
        except:
            pass

    def clear(self):
        self.animate_text = "Processing"
