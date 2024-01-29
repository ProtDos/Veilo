from kivy.config import ConfigParser
from kivy.properties import ColorProperty
from kivy.app import App


class Config:
    config = ConfigParser()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config.read("config.ini")
        # Theme config
        self.config.adddefaultsection("theme")
        self.config.setdefault("theme", "theme_style", "Light")

        self.config.adddefaultsection("language")
        self.config.setdefault("language", "default", "en")

        self.config.adddefaultsection("other")
        self.config.setdefault("other", "startup", "False")
        self.config.setdefault("other", "show_message_content", "False")

        self.config.adddefaultsection("coloring")
        self.config.setdefault("coloring", "main", "684bbf")
        self.config.setdefault("coloring", "secondary", "9b78f2")

        self.config.write()

    def get_main_color(self):
        return self.config.get("coloring", "main")

    def get_sec_color(self):
        return self.config.get("coloring", "secondary")

    def set_colors(self, main, secondary):

        theme_cls = App.get_running_app().theme_cls

        self.config.set("coloring", "main", main)
        self.config.set("coloring", "secondary", secondary)

        self.config.write()

        theme_cls.update(main, secondary)

    def get_theme_style(self):
        return self.config.get("theme", "theme_style")

    def is_startup(self):
        a = self.config.get("other", "startup")
        self.config.set("other", "startup", "False")
        self.config.write()
        return a

    def set_theme_style(self, theme_style):
        self.config.set("theme", "theme_style", theme_style)
        self.config.write()

    def set_language(self, lang):
        self.config.set("language", "default", lang)
        self.config.write()

    def get_language(self):
        a = self.config.get("language", "default")
        return a

    def lang_to_code(self, lang):
        lang = lang.lower()
        language_mapping = {
            "english": "en",
            "german": "de",
            "spanish": "es",
            "french": "fr",
            "portuguese": "pt",
            "indonesian": "id",
            "swahili": "sw"
        }
        code = language_mapping.get(lang, "en")
        return code

    def message_opt(self):
        a = self.config.get("other", "show_message_content")
        return eval(a)

    def show_messages_content(self):
        App.get_running_app().show_message_content = True
        self.config.set("other", "show_message_content", "True")
        self.config.write()

    def hide_messages_content(self):
        App.get_running_app().show_message_content = False
        self.config.set("other", "show_message_content", "False")
        self.config.write()


config = Config()
