from kivy.clock import Clock
from kivy.properties import StringProperty
from components.screen import PScreen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as gch


class Processing(PScreen):
    animate_text = StringProperty("Processing")

    win_size = StringProperty(Window.size)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = gch("#ffffff")
        Clock.schedule_interval(self.update, .6)

        print(self.win_size)

    def update(self, _):
        try:
            self.animate_text += "." if "..." not in self.animate_text else self.clear()
        except:
            pass

    def clear(self):
        self.animate_text = "Processing"
