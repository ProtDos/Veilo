import webbrowser

from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from utils.configparser import config


class Swap(PScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def cont(self):
        pass
