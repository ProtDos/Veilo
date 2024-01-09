import os
import random
import kivy.core.audio
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ColorProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from components.label import PLabel
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from core.theming import ThemableBehavior

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from PIL import Image
from kivy.graphics import Color, RoundedRectangle


def resize_image(original_width, original_height, target_width, target_height):
    aspect_ratio = original_width / original_height

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
    padding: [dp(5), dp(4)]
    spacing: dp(20)
          
    size_hint: None, None
    size_hint_x: .5
    height: dp(60)
        
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
        
        send_by_user: root.send_by_user

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
        
        RoundedRectangle:
            size: [3, self.sizes[0]]
            pos: [self.x + dp(60 + 0), self.center_y - root.sizes[0] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[1]]
            pos: [self.x + dp(60 + 5), self.center_y - root.sizes[1] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[2]]
            pos: [self.x + dp(60 + 10), self.center_y - root.sizes[2] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[3]]
            pos: [self.x + dp(60 + 15), self.center_y - root.sizes[3] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[4]]
            pos: [self.x + dp(60 + 20), self.center_y - root.sizes[4] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[5]]
            pos: [self.x + dp(60 + 25), self.center_y - root.sizes[5] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[6]]
            pos: [self.x + dp(60 + 30), self.center_y - root.sizes[6] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[7]]
            pos: [self.x + dp(60 + 35), self.center_y - root.sizes[7] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[8]]
            pos: [self.x + dp(60 + 40), self.center_y - root.sizes[8] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[9]]
            pos: [self.x + dp(60 + 45), self.center_y - root.sizes[9] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[10]]
            pos: [self.x + dp(60 + 50), self.center_y - root.sizes[10] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[11]]
            pos: [self.x + dp(60 + 55), self.center_y - root.sizes[11] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[12]]
            pos: [self.x + dp(60 + 60), self.center_y - root.sizes[12] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[13]]
            pos: [self.x + dp(60 + 65), self.center_y - root.sizes[13] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[14]]
            pos: [self.x + dp(60 + 70), self.center_y - root.sizes[14] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[15]]
            pos: [self.x + dp(60 + 75), self.center_y - root.sizes[15] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[16]]
            pos: [self.x + dp(60 + 80), self.center_y - root.sizes[16] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[17]]
            pos: [self.x + dp(60 + 85), self.center_y - root.sizes[17] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[18]]
            pos: [self.x + dp(60 + 90), self.center_y - root.sizes[18] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[19]]
            pos: [self.x + dp(60 + 95), self.center_y - root.sizes[19] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[20]]
            pos: [self.x + dp(60 + 100), self.center_y - root.sizes[20] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[21]]
            pos: [self.x + dp(60 + 105), self.center_y - root.sizes[21] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[22]]
            pos: [self.x + dp(60 + 110), self.center_y - root.sizes[22] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[23]]
            pos: [self.x + dp(60 + 115), self.center_y - root.sizes[23] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[24]]
            pos: [self.x + dp(60 + 120), self.center_y - root.sizes[24] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[25]]
            pos: [self.x + dp(60 + 125), self.center_y - root.sizes[25] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[26]]
            pos: [self.x + dp(60 + 130), self.center_y - root.sizes[26] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[27]]
            pos: [self.x + dp(60 + 135), self.center_y - root.sizes[27] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[28]]
            pos: [self.x + dp(60 + 140), self.center_y - root.sizes[28] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[29]]
            pos: [self.x + dp(60 + 145), self.center_y - root.sizes[29] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[30]]
            pos: [self.x + dp(60 + 150), self.center_y - root.sizes[30] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[31]]
            pos: [self.x + dp(60 + 155), self.center_y - root.sizes[31] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[32]]
            pos: [self.x + dp(60 + 160), self.center_y - root.sizes[32] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[33]]
            pos: [self.x + dp(60 + 165), self.center_y - root.sizes[33] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[34]]
            pos: [self.x + dp(60 + 170), self.center_y - root.sizes[34] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[35]]
            pos: [self.x + dp(60 + 175), self.center_y - root.sizes[35] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[36]]
            pos: [self.x + dp(60 + 180), self.center_y - root.sizes[36] / 2]
            radius: [2]
        
        RoundedRectangle:
            size: [3, self.sizes[37]]
            pos: [self.x + dp(60 + 185), self.center_y - root.sizes[37] / 2]
            radius: [2]


    
    PBoxLayout:
        adaptive_height: True
    
        PIconButton2:
            id: btn
            icon: "play_2"  # "pause"
            adaptive_height: True
            font_size: dp(25)
            y: rooot.y
            
            on_release:
                print(root.sizes)
                root.play_clicked()


<ImageMessage>
    id: rooot
    orientation: "horizontal"
    padding: [dp(10), dp(8)]
    spacing: dp(10)
          
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

        self.spacing = dp(0)

        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def open_f(self):
        PDialog(content=DownloadVerify()).open()


class AudioMessage(ButtonBehavior, ThemableBehavior, BoxLayout):
    send_by_user = BooleanProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    filename_data = StringProperty()

    sizes = ListProperty([random.randint(2, 20) for _ in range(38)])

    # siz = []
    # sizes = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.set_color, 0)
        Clock.schedule_once(self.set_thing, 0)

    def set_color(self, dt):
        # print("SIZ:", self.siz)
        self.sizes = [random.randint(2, 20) for _ in range(38)]

        print(self.sizes)
        print(self.filename_data)

        self.sound = kivy.core.audio.SoundLoader.load(self.filename_data)

        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def play_clicked(self):
        if self.ids.btn.icon == "play_2":
            self.ids.btn.icon = "pause"
            self.sound.bind(on_stop=self.sound_finished)
            self.sound.play()
        else:
            self.sound_pos = self.sound.get_pos()
            print(self.sound_pos)
            self.ids.btn.icon = "play_2"
            self.sound.stop()

    def sound_finished(self, *args):
        print("Finished")
        self.ids.btn.icon = "play_2"
        self.sound.stop()


    def set_thing(self, dt):
        pass
        # with self.canvas.after:
        #     Color(rgba=get_color_from_hex("#FFFFFF"))
        # cnt = 0
        # print(self.sizes)
        # for i in range(38):
        #     with self.canvas.after:
        #         RoundedRectangle(size=[3, self.sizes[i]],
        #                          pos=[self.x + dp(60 + cnt), (self.y + dp(29)) - self.sizes[i] / 2],
        #                          radius=[2])
        #     print(f"RoundedRectangle:\n    size: [3, self.sizes[{i}]]\n    pos: [self.x + dp(60 + {cnt}), self.center_y - root.sizes[{i}] / 2]\n    radius: [2]\n")
        #     cnt += 5
        #     # print("Added")


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
        new_width, new_height = resize_image(original_width=width, original_height=height,
                                             target_width=target_width * faktor, target_height=target_height * faktor)
        self.file_size = new_width, new_height

        if self.file_size[0] > 245:
            self.file_size[0] = 245
            self.file_size[1] = 245 / self.file_size[0] * self.file_size[1]

        print((width, height), self.file_size)


class ImageMessage_Core(ButtonBehavior, ThemableBehavior, BoxLayout):
    send_by_user = BooleanProperty()

    file_size = ListProperty()

    texture = ListProperty()

    primary = ColorProperty()
    secondary = ColorProperty()

    right_ = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print(self.texture)

        Clock.schedule_once(self.set_color, 0)
        Clock.schedule_once(self.update_image_size, 0)

        Clock.schedule_once(self.set_texture, 1)

    def set_texture(self, _):
        print(self.texture)
        self.ids.aaasd.texture = self.texture[0]
        self.ids.aaasd.reload()

    def set_color(self, dt):
        self.primary = self.theme_cls.primary_dark
        self.secondary = self.theme_cls.primary_color

    def update_image_size(self, dt):
        self.right_ = Window.size[1] - dp(8), self.y

        width, height = self.file_size
        faktor = .7
        target_width, target_height = Window.size
        new_width, new_height = resize_image(original_width=width, original_height=height,
                                             target_width=target_width * faktor, target_height=target_height * faktor)
        self.file_size = new_width, new_height

        if self.file_size[0] > 245:
            self.file_size[0] = 245
            self.file_size[1] = 245 / self.file_size[0] * self.file_size[1]

        print((width, height), self.file_size)


class DownloadVerify(PBoxLayout):
    pass
