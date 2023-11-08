from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.boxlayout import Card
from utils.configparser import config


class Pin(PScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.v1_num = None
        self.v2_num = None
        self.v3_num = None
        self.v4_num = None

        self.final = None

    def v1(self, num):
        self.v1_num = num
        self.ids.v1.disabled = True
        self.ids.v2.disabled = False

        self.ids.v2.focus = True

    def v2(self, num):
        self.v2_num = num
        self.ids.v2.disabled = True
        self.ids.v3.disabled = False

        self.ids.v3.focus = True

    def v3(self, num):
        self.v3_num = num
        self.ids.v3.disabled = True
        self.ids.v4.disabled = False

        self.ids.v4.focus = True

    def v4(self, num):
        self.v4_num = num
        self.ids.v4.disabled = True

        self.final = str(self.v1_num) + str(self.v2_num) + str(self.v3_num) + str(self.v4_num)

        print(self.final)

        self.ids.verify_button.disabled = False

    def verify_pin(self):
        pin = self.final
        self.ids.verify_button.disabled = True

    def open_sad(self):
        # TODO: Open popup for account recovery (Not possible)
        pass

