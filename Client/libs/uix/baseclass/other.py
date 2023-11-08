from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from utils.configparser import config


class Other(PScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def export_data(self):
        self.manager.set_current("export_data")

    def delete_account(self):
        self.d = PDialog(content=AccountDeletion())
        self.d.open()

    def quarantine(self):
        pass

    def swap(self):
        self.manager.set_current("account_swap")


class AccountDeletion(PBoxLayout):
    pass
