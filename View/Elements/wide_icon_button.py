from kivy.lang import Builder
from kivy.uix.button import Button
from kivymd.uix.behaviors import RectangularRippleBehavior, FakeRectangularElevationBehavior, HoverBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import *
from kivymd.uix.label import MDLabel
from kivymd.uix.tooltip import MDTooltip

from Config.otter_checker_config import OtterCheckerConfig

Builder.load_string("""
<WideIconButton>:
    pos_hint: {"center_x": .5, "center_y": .5}
    user_font_size: "18sp"
""")


class WideIconButton(MDFillRoundFlatIconButton, MDTooltip):
    def __init__(self, callback, icon_color=None, tooltip=None, **kwargs):
        super().__init__(**kwargs)
        if tooltip:
            self.tooltip_text = tooltip
        self.tooltip_display_delay = OtterCheckerConfig.instance().TOOLTIP_DELAY
        whiteness = .1
        self.icon_color = icon_color or (whiteness, whiteness, whiteness, 1)
        self.center_icon()
        self.bind(on_press=callback)

    def center_icon(self):
        for child in self.children:
            if isinstance(child, MDBoxLayout):
                child.adaptive_width = True
