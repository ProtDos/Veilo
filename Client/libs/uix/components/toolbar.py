import random
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from components.button import PIconButton, PIconButton2
from core.theming import ThemableBehavior


Builder.load_string(
    """
#: import get_color_from_hex kivy.utils.get_color_from_hex
<PToolbar>
    size_hint_y: None
    height: dp(56)
    padding: [dp(15), dp(25), dp(15), dp(10)]

    PBoxLayout:
        id: left_actions
        orientation: "horizontal"
        size_hint_x: None
        padding: [0, (self.height - dp(48)) / 2]

    PBoxLayout:
        padding: [dp(10), 0]

        PLabel:
            text: root.title
            font_size: sp(25)
            size_hint_x: None
            width: self.texture_size[0]
            text_size: None, None
            markup: True
            on_touch_down:
                if self.collide_point(*args[1].pos): \
                root.dispatch('on_title_press')

    PBoxLayout:
        id: right_actions
        orientation: "horizontal"
        size_hint_x: None
        padding: [0, (self.height - dp(48)) / 2]


<PToolbar_Chat>
    size_hint_y: None
    height: dp(56)
    padding: [dp(15), dp(25), dp(15), dp(20)]
    
    canvas.before:
        Color:
            rgba: get_color_from_hex("#ffffff")
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [0, 0, 20, 20]

    PBoxLayout:
        id: left_actions
        orientation: "horizontal"
        size_hint_x: None
        padding: [0, (self.height - dp(48)) / 2]
    
    PBoxLayout:
        padding: [dp(10),]
       
        adaptive_size: True
        pos_hint: {"center_y": .5}
        
        FitImage:
            source: root.image
            size_hint: None, None
            size: dp(40), dp(40)
            radius: [dp(15),]    
            
            on_touch_down:
                if self.collide_point(*args[1].pos): \
                root.dispatch('on_title_press')
          

    PBoxLayout:
        padding: [dp(10), 0]

        PLabel:
            text: root.title
            font_size: sp(25)
            size_hint_x: None
            width: self.texture_size[0]
            text_size: None, None
            markup: True
            on_touch_down:
                if self.collide_point(*args[1].pos): \
                root.dispatch('on_title_press')

    PBoxLayout:
        id: right_actions
        orientation: "horizontal"
        size_hint_x: None
        padding: [0, (self.height - dp(48)) / 2]
"""
)


class PToolbar(BoxLayout, ThemableBehavior):
    title = StringProperty()
    text_color = ColorProperty(None)
    left_action_items = ListProperty()
    right_action_items = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_title_press")

    def on_left_action_items(self, _, value):
        self.update_action_bar(self.ids["left_actions"], value)

    def on_right_action_items(self, _, value):
        print(self.ids["right_actions"], value)
        self.update_action_bar2(self.ids["right_actions"], value)

    @staticmethod
    def update_action_bar(action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                PIconButton(
                    icon=item[0],
                    mode="unstyled",
                    font_size="23sp",
                    pos_hint={"center_y": 0.5},
                    on_release=item[1],
                )
            )
        action_bar.width = new_width

    @staticmethod
    def update_action_bar2(action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                PIconButton2(
                    icon=item[0],
                    mode="unstyled",
                    font_size="23sp",
                    pos_hint={"center_y": 0.5},
                    on_release=item[1],
                )
            )
        action_bar.width = new_width

    def on_title_press(self):
        pass


class PToolbar_Chat(BoxLayout, ThemableBehavior):
    title = StringProperty()
    secondary_text = StringProperty()
    text_color = ColorProperty(None)
    left_action_items = ListProperty()
    right_action_items = ListProperty()

    image = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_title_press")

    def on_left_action_items(self, _, value):
        self.update_action_bar(self.ids["left_actions"], value)

    def on_right_action_items(self, _, value):
        self.update_action_bar2(self.ids["right_actions"], value)

    @staticmethod
    def update_action_bar(action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                PIconButton(
                    icon=item[0],
                    mode="unstyled",
                    font_size="23sp",
                    pos_hint={"center_y": 0.5},
                    on_release=item[1],
                    color=get_color_from_hex("#684BBF")
                )
            )
        action_bar.width = new_width

    @staticmethod
    def update_action_bar2(action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                PIconButton2(
                    icon=item[0],
                    mode="unstyled",
                    font_size="23sp",
                    pos_hint={"center_y": 0.5},
                    on_release=item[1],
                )
            )
        action_bar.width = new_width

    def on_title_press(self):
        pass

    @staticmethod
    def get_creamy_color():
        red = random.randint(200, 255)
        green = random.randint(180, 220)
        blue = random.randint(150, 200)

        return "#{:02X}{:02X}{:02X}".format(red, green, blue)
