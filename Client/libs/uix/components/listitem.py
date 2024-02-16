from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from components.boxlayout import PBoxLayout
from core.theming import ThemableBehavior
from kivy.utils import get_color_from_hex

Builder.load_string(
    """
<ListItem>
    spacing: dp(15)
    padding: dp(10)
    adaptive_height: True

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_y": .5}

        PIcon:
            icon: root.icon
            adaptive_size: True
            font_size: sp(30)

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

<AttachmentChat>
    spacing: dp(15)
    padding: [dp(5), dp(8)]
    adaptive_height: True
    
    pos: self.pos if root.send_by_user else [dp(10) + dp(10), self.y] 

    canvas.before:
        Color:
            rgba: 
                root.bg_color if self.send_by_user else root.bg_color
        RoundedRectangle:
            radius: 
                [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
                else [dp(5), dp(16), dp(16), dp(16)]
            size: self.size
            pos: self.pos

            
    on_release:
        app.download_file(root.source_)

    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_y": .5}
        
        padding: [dp(10), dp(3), dp(3), dp(3)]

        PIcon2:
            icon: root.icon
            text_color: root.text_color
            adaptive_size: True
            font_size: sp(30)

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(4)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            text_color: root.text_color
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None
            text_color_sec: root.text_color

<ListItem2>
    spacing: dp(15)
    padding: dp(10)
    adaptive_height: True

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_y": .5}

        PIcon2:
            icon: root.icon
            adaptive_size: True
            font_size: sp(30)

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None


<ListItemSwitch>
    spacing: dp(15)
    padding: dp(10)
    adaptive_height: True

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos
    
    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_y": .5, "center_x": .9}
        
        padding: [0, 0, 0, dp(20)]

        PSwitch:
            font_size: sp(30)

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None


<-ChatListItem>
    time_lbl: time_lbl
    padding: [dp(10), dp(15)]
    spacing: dp(10)
    adaptive_height: True
    
    on_touch_down:
        app.nah(args, self.text)
    
    on_touch_move:
        app.no(*args)
    
    on_touch_up:
        app.noo(*args, self.text)
    
    
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    PBoxLayout:
       
        adaptive_size: True
        pos_hint: {"center_y": .5}

        FitImage:
            source: root.image
            size_hint: None, None
            size: dp(50), dp(50)
            radius: [dp(18),]

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.display
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: "@" + root.text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_size: True
        pos_hint: {"center_y": .5}

        PLabel:
            id: time_lbl
            text: root.time
            font_name: 'LexendThin'
            adaptive_size: True

        Widget:
            size_hint: None, None
            size: dp(15), dp(15)

            canvas.before:
                Color:
                    rgba:
                        root.theme_cls.primary_color if root.unread_messages \
                        else (0, 0, 0, 0)
                Ellipse:
                    size: self.size
                    pos: self.x + time_lbl.width - dp(12), self.y - dp(8)


<-GroupListItem>
    padding: [dp(10), dp(15)]
    spacing: dp(5)
    adaptive_height: True
    
    on_press:
        app.select(*args)
        
    canvas.before:
        Color:
            rgba: [0, 0, 0, 0]
        Rectangle:
            pos: self.pos
            size: self.size
    
    
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos
    
        
    PBoxLayout:   
        adaptive_size: True            
        pos_hint: {"center_y": .5}
                
        FitImage:
            id: da_img
            source: "assets/images/dummy.png"
            size_hint: None, None
            size: dp(50), dp(50)
            radius: [dp(100),]
        
        PIconButtonGroup:
            opacity: 1 if root.checked else 0
            icon: "check_circle"
            mode: "unstyled"
            font_size: sp(25)
            pos_hint: {"x": -1, "y": +0.2}

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(3)
        adaptive_height: True
        pos_hint: {"center_y": .5}
        
        padding: [dp(10), 0, 0, 0]

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None
    """
)


class ListItem(ButtonBehavior, ThemableBehavior, PBoxLayout):

    bg_color = ColorProperty([0, 0, 0, 0])

    text = StringProperty()

    secondary_text = StringProperty()

    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.theme_cls.bind(theme_style=self._update_bg_color)

        self.long_press_time = 1  # Time threshold for long press in seconds
        self.long_press_event = None

    def _update_bg_color(self, *_):
        self.bg_color = self.theme_cls.bg_normal

    def on_state(self, _, value):
        Animation(
            bg_color=self.theme_cls.bg_dark
            if value == "down"
            else self.theme_cls.bg_normal,
            d=0.1,
            t="in_out_cubic",
        ).start(self)


class AttachmentChat(ButtonBehavior, ThemableBehavior, PBoxLayout):
    bg_color = ColorProperty([0, 0, 0, 0])

    text = StringProperty()

    source_ = StringProperty()

    secondary_text = StringProperty()

    icon = StringProperty()

    text_color = ColorProperty(get_color_from_hex("#D9DADF"))
    text_color_sec = ColorProperty(get_color_from_hex("#D9DADF"))

    send_by_user = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.theme_cls.bind(theme_style=self._update_bg_color)


    def _update_bg_color(self, *args):
        self.bg_color = self.theme_cls.bg_normal



class ListItem2(ButtonBehavior, ThemableBehavior, PBoxLayout):

    bg_color = ColorProperty([0, 0, 0, 0])

    text = StringProperty()

    secondary_text = StringProperty()

    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.theme_cls.bind(theme_style=self._update_bg_color)

        self.long_press_time = 1
        self.long_press_event = None

    def _update_bg_color(self, *_):
        self.bg_color = self.theme_cls.bg_normal

    def on_state(self, _, value):
        Animation(
            bg_color=self.theme_cls.bg_dark
            if value == "down"
            else self.theme_cls.bg_normal,
            d=0.1,
            t="in_out_cubic",
        ).start(self)


class ListItemSwitch(ButtonBehavior, ThemableBehavior, PBoxLayout):

    bg_color = ColorProperty([0, 0, 0, 0])

    text = StringProperty()

    secondary_text = StringProperty()

    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.theme_cls.bind(theme_style=self._update_bg_color)

        self.long_press_time = 1
        self.long_press_event = None

    def _update_bg_color(self, *_):
        self.bg_color = self.theme_cls.bg_normal

    def on_state(self, _, value):
        Animation(
            bg_color=self.theme_cls.bg_dark
            if value == "down"
            else self.theme_cls.bg_normal,
            d=0.1,
            t="in_out_cubic",
        ).start(self)


class ChatListItem(ListItem):
    image = StringProperty()

    display = StringProperty()

    name = StringProperty()

    time = StringProperty()

    unread_messages = BooleanProperty()


class GroupListItem(ListItem):
    image = StringProperty()

    name = StringProperty()

    time = StringProperty()

    unread_messages = BooleanProperty()

    bg_color = ColorProperty([0, 0, 0, 0])

    real_bg_color = ColorProperty([0, 0, 0, 0])

    checked = BooleanProperty()
