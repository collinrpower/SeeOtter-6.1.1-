from kivy.lang import Builder
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from Config.otter_checker_config import OtterCheckerConfig

Builder.load_string("""
<CircleIconButton>:                   
    pos_hint: {"center_x": .5, "center_y": .5}
    user_font_size: "24sp"
""")


class CircleIconButton(MDIconButton, MDTooltip):

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.tooltip_display_delay = OtterCheckerConfig.instance().TOOLTIP_DELAY
        self.bind(on_press=callback)
        self._radius = 10
