from kivy.lang import Builder
from kivy.properties import ColorProperty, StringProperty, ListProperty
from kivy.uix.label import Label
from components.adaptive_widget import AdaptiveWidget
from core.theming import ThemableBehavior

Builder.load_string(
    """
#: import md_icons kivymd.icon_definitions
#: import icons core.icon_definitions.icons
#:import images_path kivymd.images_path

<PLabel>
    font_name: 'Lexend'
    color:
        self.text_color if self.text_color \
        else self.theme_cls.text_color

<PIcon>
    text: u'{}'.format(icons[self.icon]) if self.icon in icons else ''
    font_name: 'Icons'
    font_size: sp(40)

<PIcon2>
    text: '{}'.format(self.icon)
    font_name: 'Iconly'
    font_size: sp(40)
"""
)


class PLabel(ThemableBehavior, AdaptiveWidget, Label):
    text_color = ColorProperty(None)
    translated_text = StringProperty()
    testtest = ListProperty()
    text = translated_text


class PIcon(PLabel):
    icon = StringProperty()


class PIcon2(PLabel):
    icon = StringProperty()
