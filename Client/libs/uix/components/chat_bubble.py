import os
import random

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty

from components.label import PLabel
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
# from components.listitem import ListItem2, AttachmentChat

from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from core.theming import ThemableBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from PIL import Image


def resize_image(original_width, original_height, target_width, target_height):
    aspect_ratio = original_width / original_height

    # Calculate the new dimensions while preserving aspect ratio
    if aspect_ratio > 1:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    return [new_width, new_height]


Builder.load_string(
    """
#: import get_color_from_hex kivy.utils.get_color_from_hex
#: import RGBA kivy.utils.rgba
#: import random random

<ChatBubble>
    adaptive_height: True
    padding: [dp(16), dp(10)]
    text_color: 1, 1, 1, 1
    text_size: self.width, None
    
    markup: True
    on_ref_press:
        app.open_link(*args)

    canvas.before:
        Color:
            rgba:
                root.primary if self.send_by_user else root.secondary
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius:
                [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
                else [dp(5), dp(16), dp(16), dp(16)]
                
                
<ChatBubble2>
    padding: [dp(10), dp(8)]
    spacing: dp(0)
    adaptive_height: True
    id: lll
    
    size_hint: None, None
    size_hint_x: root.width_set
    # width: dp(50)
    
    canvas.before:
        Color:
            rgba:
                root.primary if self.send_by_user else root.secondary
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius:
                [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
                else [dp(5), dp(16), dp(16), dp(16)]
                

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(0)
        
        adaptive_height: True

        PLabel:
            id: txt
            text: root.text
            
            size_hint: None, None
            size: lll.width * .95, 80
            
            adaptive_height: True
            
            padding: [dp(8), dp(2)]
            
            text_color: 1, 1, 1, 1
            text_size: self.width, None
            
            markup: True
            on_ref_press:
                app.open_link(*args)
        
        PLabel:
            text: "NOW"
            size_hint: None, None
            font_name: 'LexendLight'
            text_color: get_color_from_hex("#D9DADF")
            
            adaptive_height: True
            
            text_size: self.width, None
            font_size: dp(10)
            padding: [dp(8), dp(2)]
        
    PBoxLayout:
        # adaptive_height: True
        orientation: "vertical"
        spacing: dp(0)
        pos_hint: {"center_y": .5}
            
        Widget:   
            size_hint: None, None
            height: dp(txt.height)
            
        PIcon2:
            icon: root.icon
            
            adaptive_height: True
            
            opacity: 1 if root.send_by_user else 0
            
            font_size: dp(15)
            text_color: get_color_from_hex(root.icon_color)
            # text_color: root.icon_color
            
            pos_hint: {"center_x": .9}

<Attachment>
    orientation: "horizontal"
    pos_hint: {"right": 1}
    padding: [dp(10), dp(8)]
    spacing: dp(10)
      
    size_hint: None, None
    size_hint_x: .5
    
    on_release:
        root.open_f()
    
        
    
    AttachmentChat:
        bg_color: root.primary if root.send_by_user else root.secondary
        icon: "file_earmark"
        text: root.base
        text_color: get_color_from_hex("#FFFFFF")
        text_color_sec: get_color_from_hex("#808080")
        secondary_text: root.file_size
        source_: root.source_

<AudioMessage>
    id: rooot
    orientation: "horizontal"
    pos_hint: {"right": 1}
    
    padding: [dp(10), dp(8)]
    spacing: dp(10)
    
    size_hint: None, None
    size_hint_x: .8
    height: dp(60)       
        
    canvas:
        Color:
            rgba:
                root.primary if self.send_by_user else root.secondary
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius:
                [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
                else [dp(5), dp(16), dp(16), dp(16)]
          

        Color:
            rgba: 
                get_color_from_hex("#FFFFFF")
    
    PBoxLayout:
        adaptive_height: True
    
        PIconButton2:
            id: btn
            icon: "play_2"  # "pause"
            adaptive_height: True
            font_size: dp(25)
            y: rooot.y
            
            on_release:
                root.play_clicked()

<ImageMessage>
    id: rooot
    orientation: "horizontal"
    padding: [dp(10), dp(8)]
    spacing: dp(10)
    
    pos_hint: {"right": 1}
    
    
    size_hint: None, None
    width: dp(root.file_size[0])    
    height: dp(root.file_size[1])
    
    canvas.before:
        Color:
            rgba:
                root.primary if self.send_by_user else root.secondary
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius:
                [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
                else [dp(5), dp(16), dp(16), dp(16)]    
        
    # canvas:
    #     Color:
    #         rgba:
    #             root.primary if self.send_by_user else root.secondary
    #     RoundedRectangle:
    #         size: self.size
    #         pos: root.right_ if root.send_by_user else [dp(10), self.y]
    #         radius:
    #             [dp(16), dp(5), dp(16), dp(16)] if self.send_by_user \
    #             else [dp(5), dp(16), dp(16), dp(16)]
    
    on_release:
        app.open_file(root.source)
    
    FitImage:
        source: root.source
        radius: [dp(16), dp(16), dp(16), dp(16), ] 
        pos: self.pos if root.send_by_user else [dp(10) + dp(10), self.y] 

<DownloadVerify>
    otth: otth

    orientation: "vertical"
    adaptive_height: True
    padding: dp(10)
    spacing: dp(10)

    PLabel:
        original: "HOLD UP"
        text: self.original if app.language == 'EN' else app.translate(self.original)

        halign: "center"
        font_name: "LexendMedium"
        adaptive_height: True
        font_size: sp(30)

    PLabel:
        original: "This file"
        text: self.original if app.language == 'EN' else app.translate(self.original)

        halign: "center"
        font_name: "LexendLight"
        font_size: sp(15)
        adaptive_height: True
        text_size: self.width, None

    PLabel:
        text: root.message
        halign: "center"
        font_name: "LexendLight"
        font_size: sp(13)
        adaptive_height: True
        text_size: self.width, None
        color: 0.5, 0.5, 0.5, 1

    PLabel:
        original: "is potentially dangerous. Are you sure you want to continue?"
        text: self.original if app.language == 'EN' else app.translate(self.original)
        halign: "center"
        font_name: "LexendLight"
        font_size: sp(15)
        adaptive_height: True
        text_size: self.width, None

    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_x": .5}
        spacing: dp(10)

        PButton:
            id: otth
            original: "Cancel"
            text: self.original if app.language == 'EN' else app.translate(self.original)
            on_release:
                app.dismiss()

        PButton:
            original: "Yep!"
            text: self.original if app.language == 'EN' else app.translate(self.original)
            mode: "outlined"
            size_hint_x: None
            width: otth.width
            on_release:
                app.dismiss()
                webbrowser.open(root.message)
"""
)


class ChatBubble(PLabel):
    send_by_user = BooleanProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)

    def set_color(self, dt):
        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color


class ChatBubble2(ButtonBehavior, ThemableBehavior, PBoxLayout):
    send_by_user = BooleanProperty()

    text = StringProperty()

    secondary_text = StringProperty("")

    icon = StringProperty("clock")  # check_circle
    width_set = NumericProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    icon_color = StringProperty("#BABBBF")

    uid = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)

    def set_color(self, dt):
        # self.icon_color = get_color_from_hex("#fc050d")

        print(self.ids.txt.texture_size)
        thresholds = [3, 7, 10, 13, 16, 19]
        widths = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        l = len(self.text)

        for i, threshold in enumerate(thresholds):
            if l <= threshold:
                self.width_set = widths[i]
                break
        else:
            self.width_set = widths[-1]

        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color


class Attachment(ButtonBehavior, ThemableBehavior, PBoxLayout):
    send_by_user = BooleanProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    source_ = StringProperty()

    filename = StringProperty()
    base = StringProperty("")
    file_size = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)

    def set_color(self, dt):
        print("Yup")
        self.base = os.path.basename(self.filename)

        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def open_f(self):
        PDialog(content=DownloadVerify()).open()


class AudioMessage(ButtonBehavior, ThemableBehavior, BoxLayout):
    send_by_user = BooleanProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    sizes = [random.randint(2, 20) for _ in range(38)]
    # siz = []
    # sizes = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)
        Clock.schedule_once(self.set_thing, 0)

    def set_color(self, dt):
        # print("SIZ:", self.siz)
        self.sizes = [random.randint(2, 20) for _ in range(38)]

        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def play_clicked(self):
        if self.ids.btn.icon == "play_2":
            self.ids.btn.icon = "pause"
        else:
            self.ids.btn.icon = "play_2"

    def set_thing(self, dt):
        self.canvas.add(Color(rgba=get_color_from_hex("#FFFFFF")))

        cnt = 0

        for i in range(38):
            self.canvas.add(
                RoundedRectangle(size=[3, self.sizes[i]], pos=[self.x + dp(60 + cnt), (self.y + dp(29)) - self.sizes[i] / 2],
                                 radius=[2]))
            cnt += 5


class LineWidget(Widget):
    send_by_user = BooleanProperty()

    text = StringProperty()

    secondary_text = StringProperty("")

    icon = StringProperty("clock")  # check_circle

    primary = ColorProperty()
    secondary = ColorProperty()

    is_image = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(LineWidget, self).__init__(**kwargs)

        with self.canvas:
            Color(0, 0, 0)

            num_lines = 38
            line_spacing = self.height / (num_lines - 20)

            line_width = 5

            line_radius = 3

            for i in range(num_lines):
                line_height = random.randint(2, 20)

                y = (self.center_x - line_width / 2) - line_height / 2
                x = (i + 1) * line_spacing

                RoundedRectangle(pos=(x, y), size=(line_width, line_height), radius=[line_radius])


class ImageMessage(ButtonBehavior, ThemableBehavior, BoxLayout):
    send_by_user = BooleanProperty()

    source = StringProperty()
    file_size = ListProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    right_ = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)
        Clock.schedule_once(self.update_image_size, 0)

    def set_color(self, dt):
        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def update_image_size(self, dt):
        self.right_ = Window.size[1] - dp(8), self.y

        width, height = self.file_size
        faktor = .7
        target_width, target_height = Window.size
        new_width, new_height = resize_image(original_width=width, original_height=height, target_width=target_width * faktor, target_height=target_height * faktor)
        self.file_size = new_width, new_height

        if self.file_size[0] > 245:
            self.file_size[0] = 245
            self.file_size[1] = 245 / self.file_size[0] * self.file_size[1]

        print((width, height), self.file_size)


class DownloadVerify(PBoxLayout):
    pass
