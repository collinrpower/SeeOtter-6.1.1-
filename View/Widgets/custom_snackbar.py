from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import BaseSnackbar

Builder.load_string('''
<CustomSnackbar>

    MDIconButton:
        pos_hint: {'center_y': .5}
        icon: root.icon
        theme_text_color: 'Custom'
        text_color: root.icon_color
        opposite_colors: False

    MDLabel:
        id: text_bar
        size_hint_y: None
        height: self.texture_size[1]
        text: root.text
        font_size: root.font_size
        theme_text_color: 'Custom'
        text_color: 'ffffff'
        shorten: True
        shorten_from: 'right'
        pos_hint: {'center_y': .5}
''')


class CustomSnackbar(BaseSnackbar):

    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")
    icon_color = ObjectProperty((1, 1, 1, 1))
    bg_color = ObjectProperty((1, 1, 1, .1))
