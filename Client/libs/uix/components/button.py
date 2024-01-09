from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ColorProperty, OptionProperty, StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior


from components.label import PIcon, PIcon2, PLabel
from core.theming import ThemableBehavior
from kivy.utils import get_color_from_hex

Builder.load_string(
"""
#: import get_color_from_hex kivy.utils.get_color_from_hex

<PButton>
    size_hint: None, None
    size: self.texture_size[0] + dp(10), self.texture_size[1] + dp(10)
    padding: [dp(10), dp(10)]
    font_size: sp(16)

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    canvas.after:
        Color:
            rgba: 0.5, 0.5, 0.5, 0.5
        Line:
            width: dp(1)
            rounded_rectangle:
                (self.x, self.y, self.width, self.height, dp(18))
<PSwitch>
    size_hint: None, None
    size: dp(24), dp(40)
    padding: [dp(10), dp(10)]
    font_size: sp(16)
        
    canvas.before:
        Color:
            rgba: get_color_from_hex("#D0021B") if self.status == "off" else get_color_from_hex("#4F7041")
        Ellipse:
            angle_start: 180
            angle_end: 360
            pos: self.pos[0] - self.size[1] / 2, self.pos[1]
            size: self.size[1], self.size[1]
        Ellipse:
            angle_start: 360
            angle_end: 540
            pos: self.size[0] + self.pos[0] - self.size[1]/2.0, self.pos[1]
            size: self.size[1], self.size[1]
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba:
                root.foreground_color if self.text \
                else (0.5, 0.5, 0.5, 0.5)
                
                
        Line:  # below
            width: dp(1)    
            points: (self.pos[0], self.pos[1], self.size[0] + self.pos[0], self.pos[1])          
            
        Line:  # top
            width: dp(1)    
            points: (self.pos[0], self.pos[1] + self.size[1], self.size[0] + self.pos[0], self.pos[1] + self.size[1])           
            
        Line:  # left
            width: dp(1)
            ellipse: (self.pos[0] - self.size[1]/2.0, self.pos[1], self.size[1], self.size[1], 180, 360)
        
        Line:  # right
            width: dp(1)    
            ellipse: (self.size[0] + self.pos[0] - self.size[1]/2.0, self.pos[1], self.size[1], self.size[1], 360, 540)
            
        # creating the circle for the slider
        Color:
            rgba: get_color_from_hex("#D9E0D3") if self.status == "off" else get_color_from_hex("#D9E0D3")
        Ellipse:
            id: my_el
            pos: (self.pos[0] - self.size[1]/2.0 + dp(5), self.pos[1] + dp(5)) if self.status == "off" else (self.size[0] + self.pos[0] - self.size[1]/2.0 + dp(5), self.pos[1] + dp(5))
            # size: (self.size[1] - dp(20), self.size[1] - dp(20)) if self.status == "off" else (self.size[1] - dp(10), self.size[1] - dp(10))
            size: self.size[1] - dp(10), self.size[1] - dp(10)

            angle_start: 0
            angle_end: 360
    
    on_release:
        self.slide()
            

    #canvas.before:
    #    Color:
    #        rgba: get_color_from_hex("#D9E0D3")
    #    RoundedRectangle:
    #        radius: [dp(30),]
    #        size: self.size
    #        pos: self.pos
    #    Color:
    #        rgba: get_color_from_hex("#B0B7A9")
    #    Line:
    #        width: dp(1)
    #        rounded_rectangle: (self.x, self.y, self.width, self.height, dp(30))


<PIconButton>
    size_hint: None, None
    size: self.texture_size
    padding: [dp(10), dp(10)]

    canvas.before:
        Color:
            rgba: self.bg_color
        Ellipse:
            size: self.size
            pos: self.pos

    canvas.after:
        Color:
            rgba: 0.5, 0.5, 0.5, 0.5
        Line:
            ellipse: (self.x, self.y, self.width, self.height)
            width: dp(1)
            
<PIconButton2>
    size_hint: None, None
    size: self.texture_size
    padding: [dp(10), dp(10)]

    canvas.before:
        Color:
            rgba: self.bg_color
        Ellipse:
            size: self.size
            pos: self.pos

    canvas.after:
        Color:
            rgba: 0.5, 0.5, 0.5, 0.5
        Line:
            ellipse: (self.x, self.y, self.width, self.height)
            width: dp(1)

<PIconButtonGroup>
    size_hint: None, None
    size: dp(2), dp(2)

    canvas.before:
        Color:
            rgba: self.bg_color
        Ellipse:
            size: self.size
            pos: self.pos

    canvas.after:
        Color:
            rgba: 0.5, 0.5, 0.5, 0.5
        Line:
            ellipse: (self.x, self.y, self.width, self.height)
            width: dp(1)
"""
)


class BaseButton(ButtonBehavior, ThemableBehavior):
    mode = OptionProperty(
        "contained", options=["contained", "outlined", "unstyled", "custom"]
    )

    bg_color = ColorProperty([0, 0, 0, 0])

    bg_normal = ColorProperty([0, 0, 0, 0])

    bg_down = ColorProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self.on_mode(None, self.mode))
        self.theme_cls.bind(
            theme_style=lambda *args: self.on_mode(None, self.mode)
        )

    def on_mode(self, *args):
        raise NotImplementedError()

    def on_state(self, instance, value):
        anim = Animation(
            bg_color=self.bg_down if value == "down" else self.bg_normal,
            d=0.2,
            t="in_out_cubic",
        )
        anim.start(self)


class PButton(BaseButton, PLabel):
    def on_mode(self, instance, value):
        if value == "contained":
            self.canvas.after.clear()
            self.bg_color = self.theme_cls.primary_color
            self.bg_normal = self.theme_cls.primary_color
            self.bg_down = self.theme_cls.primary_dark
            self.text_color = (1, 1, 1, 1)
        elif value == "outlined":
            self.bg_down = (0.5, 0.5, 0.5, 0.5)
            self.bg_normal = self.theme_cls.bg_normal
            self.bg_color = self.theme_cls.bg_normal
        elif value == "custom":
            self.canvas.after.clear()
            self.bg_color = self.bg_normal


class PIconButton(BaseButton, PIcon):
    def on_mode(self, instance, value):
        if value == "contained":
            self.canvas.after.clear()
            self.bg_color = self.theme_cls.primary_color
            self.bg_normal = self.theme_cls.primary_color
            self.bg_down = self.theme_cls.primary_dark
            self.text_color = (1, 1, 1, 1)
        elif value == "outlined":
            self.bg_down = self.theme_cls.bg_dark
            self.bg_normal = self.theme_cls.bg_normal
            self.bg_color = self.theme_cls.bg_normal
        elif value == "unstyled":
            self.bg_down = self.theme_cls.bg_dark
            Clock.schedule_once(lambda x: self.canvas.after.clear())
        else:
            self.bg_color = self.bg_normal
            Clock.schedule_once(lambda x: self.canvas.after.clear())


class PIconButton2(BaseButton, PIcon2):
    def on_mode(self, instance, value):
        if value == "contained":
            self.canvas.after.clear()
            self.bg_color = self.theme_cls.primary_color
            self.bg_normal = self.theme_cls.primary_color
            self.bg_down = self.theme_cls.primary_dark
            self.text_color = (1, 1, 1, 1)
        elif value == "outlined":
            self.bg_down = self.theme_cls.bg_dark
            self.bg_normal = self.theme_cls.bg_normal
            self.bg_color = self.theme_cls.bg_normal
        elif value == "unstyled":
            self.bg_down = self.theme_cls.bg_dark
            Clock.schedule_once(lambda x: self.canvas.after.clear())
        else:
            self.bg_color = self.bg_normal
            Clock.schedule_once(lambda x: self.canvas.after.clear())


class PIconButtonGroup(BaseButton, PIcon2):
    def on_mode(self, instance, value):
        if value == "contained":
            self.canvas.after.clear()
            self.bg_color = self.theme_cls.primary_color
            self.bg_normal = self.theme_cls.primary_color
            self.bg_down = self.theme_cls.primary_dark
            self.text_color = (1, 1, 1, 1)
        elif value == "outlined":
            self.bg_down = self.theme_cls.bg_dark
            self.bg_normal = self.theme_cls.bg_normal
            self.bg_color = self.theme_cls.bg_normal
        elif value == "unstyled":
            self.bg_down = self.theme_cls.bg_dark
            Clock.schedule_once(lambda x: self.canvas.after.clear())
        else:
            self.bg_color = self.bg_normal
            Clock.schedule_once(lambda x: self.canvas.after.clear())


class PSwitch(PButton):
    mode = "custom"
    status = StringProperty("on")

    def slide(self):
        if self.status == "on":
            self.status = "off"
        else:
            self.status = "on"

        print(self.ids.my_el.pos)

