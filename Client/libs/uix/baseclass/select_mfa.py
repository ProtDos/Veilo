from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.boxlayout import Card
from kivymd.uix.card import MDCard
from utils.configparser import config


class SelectMFA(PScreen):
    theme_icon = StringProperty()
    colorcolor = "#FFFFFF"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


