from functools import partial
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.draw_annotation_menu_button import DrawAnnotationMenuButton
from View.Elements.rounded_card import RoundedCard


class DrawAnnotationPanel(RoundedCard):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.size_hint = (None, .85)
        self.width = 200
        self.build()
        self.draw_mode_changed()
        self.bind_events()

    def build(self):
        self.layout = MDBoxLayout(orientation="horizontal", spacing=10)
        self.draw_mode_button = DrawAnnotationMenuButton(callback=self.draw_button_pressed)
        self.layout.add_widget(self.draw_mode_button)
        self.dropdown = DropDown()
        self.update_categories()
        default_category = self.controller.current_annotation_category or "None"
        self.mainbutton = MDFlatButton(text=default_category, size_hint=(1, .85))
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.layout.add_widget(self.mainbutton)
        self.add_widget(self.layout)

    def bind_events(self):
        self.mainbutton.bind(on_release=self.dropdown.open)
        self.controller.bind(mode=self.on_mode_changed)
        self.controller.bind(annotation_categories=self.update_categories)
        self.controller.bind(current_annotation_category=self.update_current_category_label)

    def update_current_category_label(self, *args):
        self.mainbutton.text = self.controller.current_annotation_category

    def update_categories(self, *args):
        print("update categories")
        for category_name, category_id in self.controller.annotation_categories:
            btn = Button(text=category_name, size_hint_y=None, height=44)
            btn.bind(on_release=partial(self.controller.set_current_annotation_category, category_name, category_id))
            self.dropdown.add_widget(btn)

    def on_mode_changed(self, *args):
        print(f"On mode changed (draw annotation panel)")
        self.draw_mode_changed()

    def draw_button_pressed(self, instance):
        print("Draw button pressed")
        self.controller.toggle_draw_mode()

    def draw_mode_changed(self, *args):
        print(f"Draw mode changed: {self.controller.draw_mode}")
        self.mainbutton.disabled = not self.controller.draw_mode
        self.draw_mode_button.set_active(self.controller.draw_mode)
