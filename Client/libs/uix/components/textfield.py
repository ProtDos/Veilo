from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.textinput import TextInput

from core.theming import ThemableBehavior

Builder.load_string(
    """

<PTextField>
    multiline: False
    password_mask: '•'
    font_name: 'Lexend'
    background_active: 'assets/images/transparent.png'
    background_normal: 'assets/images/transparent.png'
    cursor_color: self.theme_cls.primary_color
    padding: [0, dp(10), 0, 0]
    
    

    canvas.before:
        Color:
            rgba: 239, 239, 239, 0.8
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

<PTextFieldBig>
    multiline: True
    password_mask: '•'
    font_name: 'Lexend'
    background_active: 'assets/images/transparent.png'
    background_normal: 'assets/images/transparent.png'
    cursor_color: self.theme_cls.primary_color
    padding: [0, dp(10), 0, 0]
    
    
    canvas.before:
        Color:
            rgba: 239, 239, 239, 0.8
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
"""
)


class PTextField(ThemableBehavior, TextInput):
    def shake(self):
        Animation.stop_all(self)
        (
                    Animation(
                        translate_x=50,
                        t='out_quad', d=.02
                    ) + Animation(
                        translate_x=0,
                        t='out_elastic', d=.5
                    )
        ).start(self)


class PTextFieldBig(ThemableBehavior, TextInput):
    pass
