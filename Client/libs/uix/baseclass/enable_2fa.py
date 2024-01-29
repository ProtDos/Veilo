from components.screen import PScreen
from components.toast import toast
from kivy.properties import StringProperty
from kivy.core.clipboard import Clipboard


class E2FA(PScreen):
    token = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def done(self):
        self.manager.set_current("2fa_verify")

    def copy_code(self):
        Clipboard.copy(self.token)
        toast("Copied to clipboard.")
