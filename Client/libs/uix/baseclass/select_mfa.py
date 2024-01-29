from kivy.properties import StringProperty
from components.screen import PScreen


class SelectMFA(PScreen):
    theme_icon = StringProperty()
    colorcolor = "#FFFFFF"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
