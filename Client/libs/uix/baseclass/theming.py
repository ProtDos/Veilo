from __future__ import annotations
from components.screen import PScreen
from components.dialog import PDialog
from components.boxlayout import PBoxLayout
from kivy.properties import ColorProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.behaviors import RectangularElevationBehavior
# from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.colorpicker import ColorWheel
from utils.configparser import config
from components.chat_bubble import ChatBubble2


def rgba_to_hex(rgba_tuple):
    r, g, b, a = rgba_tuple
    f = 255
    al = int(r * f), int(g * f), int(b * f), int(a * f)
    return '{:02x}{:02x}{:02x}'.format(*al)


class CustomColorWheel(ColorWheel):
    def __init__(self, **kwargs):
        super(CustomColorWheel, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')

    def on_touch_down(self, touch):
        res = super(CustomColorWheel, self).on_touch_down(touch)
        if res is None:
            self.dispatch('on_press')
        return res

    def on_touch_up(self, touch):
        super(CustomColorWheel, self).on_touch_up(touch)
        if self.collide_point(*touch.pos) and touch.grab_current is self:
            self.dispatch('on_release')
            return True

    def on_press(self):
        pass

    def on_release(self):
        pass


class Theming(PScreen):
    chat_logs = ListProperty()

    main_color = ColorProperty()
    secondary_color = ColorProperty()

    picker_color = ColorProperty(get_color_from_hex("#EEEEEE"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_color = self.theme_cls.primary_color
        self.secondary_color = self.theme_cls.primary_light

        self.ids.box.add_widget(
            ChatBubble2(text="This is an example", send_by_user=True, icon="clock", pos_hint={"right": 1}))
        self.ids.box.add_widget(
            ChatBubble2(text="Yeah", send_by_user=False, icon="clock"))

    def open_picker(self):
        PDialog(
            content=PickerDialog(
            )
        ).open()

    def update_main(self):
        for child in self.ids.box.children:
            child.primary = self.main_color
            child.secondary = self.secondary_color

    def update_sec(self):
        for child in self.ids.box.children:
            child.primary = self.main_color
            child.secondary = self.secondary_color

    def set(self):
        main = rgba_to_hex(self.main_color)
        secondary = rgba_to_hex(self.secondary_color)
        config.set_colors(main, secondary)


class MainColors(ButtonBehavior, FloatLayout, RectangularElevationBehavior):
    pass


class SecondaryColors(ButtonBehavior, FloatLayout, RectangularElevationBehavior):
    pass


class PickerDialog(PBoxLayout):
    background_color = ColorProperty()

    def update_picker(self):
        color = self.ids['colory']
        self.background_color = color.color
