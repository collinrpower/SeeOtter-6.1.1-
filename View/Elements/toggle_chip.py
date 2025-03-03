from kivy.core.window import Animation
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.chip import MDChip


class ToggleChip(MDChip):

    is_selected = BooleanProperty(defaultvalue=False)

    def __init__(self, text, obj=None, is_selected=False,
                 selected_color=(.2, .8, .2, 1),
                 unselected_color=(0, 0, .1, 1), **kwargs):
        super().__init__(**kwargs)
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.is_selected = is_selected
        self.check = True
        self.text = text
        self.obj = obj
        self.on_is_selected()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == "left":
            self.is_selected = not self.is_selected
            super().on_touch_down(touch)

    def on_is_selected(self, *args):
        print(f"Selected: {self.is_selected}")
        if self.is_selected:
            self.color = self.selected_color
        else:
            self.color = self.unselected_color
