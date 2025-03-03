from kivy.lang import Builder
from kivy.uix.button import Button
from kivymd.uix.behaviors import RectangularRippleBehavior, FakeRectangularElevationBehavior
from kivymd.uix.button import *
from kivymd.uix.tooltip import MDTooltip
from kivy.utils import get_color_from_hex

from Config.otter_checker_config import OtterCheckerConfig

Builder.load_string("""
<MDIconButton>:        
    pos_hint: {"center_x": .5, "center_y": .5}
    size_hint_x: None
    width: 20
    user_font_size: "24sp"
""")


class TransparentIconButton(MDIconButton, MDTooltip):
    def __init__(self, callback, tooltip=None, **kwargs):
        super().__init__(**kwargs)
        if tooltip:
            self.tooltip_text = tooltip
        self.tooltip_display_delay = OtterCheckerConfig.instance().TOOLTIP_DELAY
        self.bind(on_press=callback)
        self.size_hint_x = None
        self.width = 60
        #self._radius = 10
