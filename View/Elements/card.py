from kivy.lang import Builder
from kivymd.uix.button import MDTextButton, MDFloatingActionButton, MDIconButton
from kivymd.uix.card import MDCard

Builder.load_string('''
<Card>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

    adaptive_height: False
    pos_hint: {"center_x": .5, "center_y": 0}
    
    GridLayout:
    
        id: header_layout
        cols: 2
        size_hint_y: None
        height: self.minimum_height
        
        MDLabel:
            text: root.title
            font_size: 16
            bold: True
            color: app.theme_cls.primary_color
            #theme_text_color: 
            size_hint_y: None
            height: self.texture_size[1] + 5
        
    MDSeparator:
        height: "2dp"
''')


class Card(MDCard):

    def __init__(self, title, **kwargs):
        self.title = title
        super().__init__(**kwargs)
        self.header_layout = self.ids.header_layout

    def add_header_button(self, text, callback):
        self.header_layout.add_widget(
            MDTextButton(text=text, on_press=callback, font_style="Button",
                         pos_hint={"right": 1, "top": .5}, theme_text_color="Secondary")
        )
