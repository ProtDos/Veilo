from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout

from components.adaptive_widget import AdaptiveWidget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

Builder.load_string('''
<Card>:
    canvas.before:
        Color:
            rgba: 69/255,55/255,86/255,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(25),]
            
    PBoxLayout:
        padding: dp(15)
        spacing:dp(15)
        radius:dp(25)
        ripple_behavior: True
        image:''
        text:""
        items_count:""
        subtext:''
        
        Image:
            source:root.image
            
        PBoxLayout:
            orientation:'vertical'
            PLabel:
                halign:"center"
                text:root.text
                font_style:"H6"
            PLabel:
                halign:"center"
                font_style:"Caption"
                text:root.subtext
            PLabel:
                halign:"center"
                text:root.items_count
    
''')


class Card(BoxLayout):
    items_count = StringProperty()
    subtext = StringProperty()
    text = StringProperty()
    image = StringProperty()

    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.padding = (10, 10)

        self.label = Label()
        self.add_widget(self.label)

    def add_widget(self, widget, index=0, canvas=None):
        if issubclass(widget.__class__, Label):
            self.label = widget
        super(Card, self).add_widget(widget, index=index, canvas=canvas)

    def on_label(self, instance, value):
        self.label = value

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return True
        return super(Card, self).on_touch_down(touch)


class PBoxLayout(AdaptiveWidget, BoxLayout):
    pass

class PGridLayout(AdaptiveWidget, GridLayout):
    pass


class PFloatLayout(AdaptiveWidget, FloatLayout):
    pass
