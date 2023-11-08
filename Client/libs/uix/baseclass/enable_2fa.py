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


class E2FA(PScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def done(self):
        self.manager.set_current("2fa_verify")
