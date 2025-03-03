from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivymd.uix.stacklayout import MDStackLayout
from View.Elements.card import Card

Builder.load_string("""""")


class StackCard(Card):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self.size_hint_y = None
        self.layout = MDStackLayout(orientation="lr-tb", minimum_height=150, spacing=5)
        self.add_widget(self.layout)

    def add(self, widget):
        self.layout.add_widget(widget)
        #self.resize()
