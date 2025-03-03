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

Builder.load_string('''
<ToggleLabel>:
    cols: 2
    size_hint: 1, None
    height: 15

    MDLabel:
        id: label
        text: root.text
        size_hint: .9, None
        height: 20
        font_size: 15
        #size: self.texture_size
    
    RightCheckbox:
        id: checkbox
        size_hint: .1, None
        height: 20
        #size: self.texture_size

''')


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class ToggleLabel(GridLayout):

    text = StringProperty("android")

    def __init__(self, text, default, text_color=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        if text_color:
            self.ids.label.color = text_color
        self.checkbox = self.ids.checkbox
        self.height = self.checkbox.height + 6
        self.checkbox.active = default
        #self.checkbox.bind(state=on_value_changed)
