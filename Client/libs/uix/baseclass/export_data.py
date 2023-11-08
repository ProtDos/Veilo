import webbrowser

from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from utils.configparser import config


class Export(PScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected = "txt"

    def label_press(self, *args):
        if self.ids.okay.collide_point(*args[1].pos):
            webbrowser.open("https://app.protdos.com/help/data_export")

    def select(self, text):
        if "TXT" in text:
            self.selected = "txt"
            self.ids.txt.icon = "checkbox_marked_circle"
            self.ids.json.icon = "checkbox_blank_circle"
        else:
            self.selected = "json"
            self.ids.json.icon = "checkbox_marked_circle"
            self.ids.txt.icon = "checkbox_blank_circle"

    def export(self):
        print("Exporting data...")
        # TODO: Implement exporting data
