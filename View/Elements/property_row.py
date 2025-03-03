from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

Builder.load_string('''
<PropertyRow>:
    cols: 2
    size_hint: 1, None
    height: 18

    MDLabel:
        id: name_label
        text: root.name
        size_hint: root.label_size_hint_x, 1
        font_size: 14
        #size: self.texture_size

    MDLabel:
        id: value_label
        text: root.value
        size_hint: .6, 1
        font_size: 14
        #size: self.texture_size

''')


class PropertyRow(GridLayout):

    name = StringProperty("Name")
    value = StringProperty("Value")
    label_size_hint_x = NumericProperty(defaultvalue=.4)

    def __init__(self, name, value="", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value

    def set_text(self, text):
        self.value = text
