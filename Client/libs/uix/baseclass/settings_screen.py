import json
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from utils.configparser import config
from extras.help_utils import get_android_system_language


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

    def change_message_visibility(self):
        if App.get_running_app().show_message_content:
            config.hide_messages_content()
            self.ids.mess_vis.secondary_text = "False"
            self.ids.mess_vis.icon = "eye_off"
        else:
            config.show_messages_content()
            self.ids.mess_vis.secondary_text = "True"
            self.ids.mess_vis.icon = "eye"



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

        a = language_mapping.get(get_android_system_language(), "English")
        self.ids.device_lang.text = a

        if a == "en":
            self.ids.en.size_hint_y = None
            self.ids.en.height = "0dp"

    def set_language(self, lang):
        lang_to_id = config.lang_to_code(lang)
        if config.get_language() == lang_to_id:
            return
        config.set_language(lang_to_id)


    def is_marked(self, text):
        idd = config.lang_to_code(text)
        if config.get_language() == idd:
            return True
        return False


class LoginDialogContent(PBoxLayout):
    def okay(self):
        pass


class BugReport(PBoxLayout):
    pass
