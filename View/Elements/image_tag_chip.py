from kivy.properties import ObjectProperty
from kivy.uix.actionbar import ActionButton
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.chip import MDChip
from kivymd.uix.stacklayout import MDStackLayout

from View.Events.chip_tag_card_event_dispatcher import ChipTagCardEventDispatcher

default_color = (.5, .5, .5)
selected_color = (1, .5, 0)


class ImageTagChip(MDChip):

    is_selected = ObjectProperty()

    def __init__(self, tag,  **kwargs):
        super().__init__(**kwargs)
        self.tag = tag
        self.icon = "" # "tag"
        self.ids.label.label_font_size = 14
        self.text = tag.name
        self.is_selected = tag.state
        self.check = False
        self.set_state_color()
        self.event = ChipTagCardEventDispatcher()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == "left":
            self.toggle_tag_state()
            self.set_state_color()
            self.event.tag_pressed(self.tag)
            super().on_touch_down(touch)

    def toggle_tag_state(self):
        state = not self.is_selected
        self.set_tag_state(state)

    def set_tag_state(self, state):
        self.tag.state = state
        self.is_selected = state
        self.set_state_color()

    def set_state_color(self):
        self.color = selected_color if self.is_selected else default_color
