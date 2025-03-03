from kivy.lang import Builder
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard

Builder.load_string("""
<RoundedCard>:
    padding: 5
    pos_hint: {"center_x": .5, "center_y": .5}
""")


class RoundedCard(MDCard, RoundedRectangularElevationBehavior):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = "outlined"
        self.radius = 10
