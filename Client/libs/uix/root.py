import json

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager


class Root(ScreenManager):

    previous_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self._goto_previous_screen)
        with open("screens.json") as f:
            self.screens_data = json.load(f)

        self.go_home = False
        self.go_chat = False

        screen = self.screens_data["processing"]
        Builder.load_file(screen["kv"])
        exec(screen["import"])
        screen_object = eval(screen["object"])
        screen_object.name = "processing"
        self.add_widget(screen_object)

    def set_current(self, screen_name, side="left", quick=False):
        if not self.has_screen(screen_name):
            screen = self.screens_data[screen_name]
            Builder.load_file(screen["kv"])
            exec(screen["import"])
            screen_object = eval(screen["object"])
            screen_object.name = screen_name
            self.add_widget(screen_object)

        self.previous_screen = {"name": self.current, "side": side}
        self.transition.direction = side
        self.transition.duration = 0 if quick else 0.4
        self.current = screen_name

        try:
            if screen_name == "other":
                self.go_home = True
            elif screen_name == "chat":
                self.go_chat = True
            else:
                self.go_chat = False
                self.go_home = False
        except:
            pass

    def _goto_previous_screen(self, _, key, *__):
        if key == 27:
            self.goto_previous_screen()
            return True
        return False

    def goto_previous_screen(self):
        if self.go_home:
            self.set_current("home", side="right")
            return
        elif self.go_chat:
            self.set_current("home", side="right")
            return

        if self.previous_screen:
            if not self.previous_screen["name"] == "auth" or self.previous_screen["name"] == "pin":
                self.set_current(
                    self.previous_screen["name"],
                    side="right"
                    if self.previous_screen["side"] == "left"
                    else "left",
                )

                self.previous_screen = None
        else:
            self.set_current(
                "home",
                side="right"
            )
