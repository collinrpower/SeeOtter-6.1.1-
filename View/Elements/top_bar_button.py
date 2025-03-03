from kivy.lang import Builder
from kivy.uix.button import Button
from kivymd.uix.button import *

from config import ACCENT_COLOR, BUTTON_BACKGROUND_COLOR, BUTTON_FONT_SIZE

Builder.load_string("""
<TopBarButton>:                   
    pos_hint: {"center_x": .5, "center_y": .5}
    user_font_size: "16sp"
""")


class TopBarButton(MDFillRoundFlatButton):

    def __init__(self, callback, bold=True, **kwargs):
        super().__init__(**kwargs)
        self.font_size = BUTTON_FONT_SIZE
        self.color = ACCENT_COLOR
        self.background_color = BUTTON_BACKGROUND_COLOR
        self.bold = bold
        self.bind(on_press=callback)
