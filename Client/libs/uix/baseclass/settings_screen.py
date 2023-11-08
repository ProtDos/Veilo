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
from kivy.utils import platform


class FuckSnus:
    """
    Example:

    search = FuckSnus()
    search.search("test")
    """

    def __init__(self):
        pass

    def search(self, term):
        f = requests.get(f"https://beta.snusbase.com/v2/combo/{term}")
        out = f.json()["result"]
        l = []
        for item in out:
            for item2 in out[item]:
                l.append(item2)
        with open(f"output_{term}.json", "w") as file:
            json.dump(l, file)


class SettingsScreen(PScreen):
    theme_icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.change_theme_icon)

    def change_theme_icon(self, *args):
        self.theme_icon = (
            "moon" if self.theme_cls.theme_style == "Light" else "sun"
        )

    def open_about(self):
        PDialog(content=AboutDialogContent_Screen()).open()

    def change_theme(self):
        def _change_theme(i):
            self.theme_cls.theme_style = (
                "Dark" if self.theme_cls.theme_style == "Light" else "Light"
            )
            config.set_theme_style(self.theme_cls.theme_style)
            self.change_theme_icon()
        Clock.schedule_once(_change_theme, .2)

    def change_language(self):
        self.l = PDialog(content=LanguageDialogContent())
        self.l.open()

    def change_notify(self):
        pass

    def view_logins(self):
        PDialog(content=LoginDialogContent()).open()

    def change_security(self):
        pass

    def change_vpn(self):
        pass

    def open_bugreport(self):
        PDialog(content=BugReport()).open()


class AboutDialogContent_Screen(PBoxLayout):
    pass


class LanguageDialogContent(PBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        language_mapping = {
            'en': 'English',
            'es': 'Spanish',
            'de': 'German',
            'fr': 'French',
        }

        a = language_mapping.get(self.get_device_language(), "English")
        self.ids.device_lang.text = a

        if a == "en":
            self.ids.en.size_hint_y = None
            self.ids.en.height = "0dp"

    def set_language(self, lang):
        print("-----------")
        print(lang)
        lang_to_id = config.lang_to_code(lang)
        print(lang_to_id)
        if config.get_language() == lang_to_id:
            print("nah")
            return
        config.set_language(lang_to_id)
        print("-----------")

    def get_device_language(self):
        if platform == 'android':
            from jnius import autoclass
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            resources = context.getResources()
            configuration = resources.getConfiguration()
            locale = configuration.locale
            return locale.getLanguage()
        else:
            return 'en'

    def is_marked(self, text):
        idd = config.lang_to_code(text)
        print(idd, config.get_language())
        if config.get_language() == idd:
            print("yey")
            return True
        return False


class LoginDialogContent(PBoxLayout):
    def okay(self):
        print("asdf")


class BugReport(PBoxLayout):
    pass
