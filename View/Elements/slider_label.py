from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.slider import MDSlider

Builder.load_string('''
<SliderLabel>:

    rows: 2
    size_hint: 1, None
    height: 55
    
    MDLabel:

        id: label
        text: root.text
        size_hint: 1, None
        font_size: 15
        height: 25
        #size: self.texture_size

    GridLayout:
        cols: 2
        size_hint: 1, None
        height: 25

        RightSlider:
            id: slider
            size_hint: .8, 1
            min: 0
            max: 1
            color: app.theme_cls.accent_color
            show_off: True
            hint: False
        MDLabel:
            text: f"{slider.value:.02f}"
            size_hint: .2, 1
            width: 50
''')


class RightSlider(IRightBodyTouch, MDSlider):
    pass


class SliderLabel(GridLayout):

    text = StringProperty()

    def __init__(self, text, prop, **kwargs):
        super().__init__(**kwargs)
        self.slider = self.ids.slider
        self.text = text
        self.prop = prop
        self.slider.value = prop
