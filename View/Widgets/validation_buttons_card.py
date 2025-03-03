from abc import ABC
from functools import partial
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from SurveyEntities.object_prediction_data import ValidationState
from View.Elements.circle_icon_button import CircleIconButton
from View.Elements.rounded_card import RoundedCard
from View.Elements.stack_card import StackCard
from View.Elements.validation_level_button import ValidationLevelButton


class ValidationButtonsCard(RoundedCard):

    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = None
        self.width = 182
        self.controller = controller
        self.dropdown_visible = False
        self.build()
        self.bind_events()

    def build(self):
        layout = MDBoxLayout(orientation="horizontal", spacing=15, size_hint=(.95, .95))
        self.validation_confidence_dropdown = DropDown()
        self.validation_confidence_dropdown.add_widget(Label(text="Confidence Level", size_hint_y=None, height=38))
        self.validation_confidence_dropdown.add_widget(
            ValidationLevelButton(text="High [1]", background_color=[0, 1, 0],
                                  on_press=self.set_high_ambiguous_level))
        self.validation_confidence_dropdown.add_widget(
            ValidationLevelButton(text="Medium [2]", background_color=[1, 1, 0],
                                  on_press=self.set_medium_ambiguous_level))
        self.validation_confidence_dropdown.add_widget(
            ValidationLevelButton(text="Low [3]", background_color=[1, 0, 0],
                                  on_press=self.set_low_ambiguous_level))
        self.validate_true_button = CircleIconButton(
            callback=partial(self.controller.validate_current_selection, ValidationState.CORRECT),
            md_bg_color=self.controller.config.ANNOTATION_CORRECT_COLOR,
            icon="check-circle",
            tooltip_text="Mark current prediction 'Valid'")
        self.validate_false_button = CircleIconButton(
            callback=partial(self.controller.validate_current_selection, ValidationState.INCORRECT),
            icon="close-circle",
            md_bg_color=self.controller.config.ANNOTATION_INCORRECT_COLOR,
            tooltip_text="Mark current prediction 'Invalid'")
        self.validate_ambiguous_button = CircleIconButton(
            callback=self.on_ambiguous_validation_pressed,
            icon="chat-question",
            md_bg_color=self.controller.config.ANNOTATION_AMBIGUOUS_COLOR,
            tooltip_text="Mark current prediction 'Ambiguous'")
        layout.add_widget(self.validate_true_button)
        layout.add_widget(self.validate_false_button)
        layout.add_widget(self.validate_ambiguous_button)
        self.add_widget(layout)

    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.close_dropdown()
        else:
            self.open_dropdown()

    def on_ambiguous_validation_pressed(self, *args):
        self.set_ambiguous_validation()

    def close_dropdown(self):
        if self.dropdown_visible:
            self.validation_confidence_dropdown.dismiss()
        else:
            print("Warning, tried to close dropdown that was already closed")

    def open_dropdown(self):
        if not self.dropdown_visible:
            self.validation_confidence_dropdown.open(self)
            self.dropdown_visible = True
        else:
            print("Warning, tried to open dropdown that was already open")

    def set_low_ambiguous_level(self, *args):
        self.close_dropdown()
        self.set_ambiguous_validation()

    def set_medium_ambiguous_level(self, *args):
        self.close_dropdown()
        self.set_ambiguous_validation()

    def set_high_ambiguous_level(self, *args):
        self.close_dropdown()
        self.set_ambiguous_validation()

    def set_ambiguous_validation(self, *args):
        self.controller.validate_current_selection(validation_state=ValidationState.AMBIGUOUS)

    def on_disabled(self, instance, value):
        """
        Not sure why, but the color defaults to grey after switching from draw mode without this.
        """
        disabled = value
        if not disabled:
            self.validate_true_button.md_bg_color = self.controller.config.ANNOTATION_CORRECT_COLOR
            self.validate_false_button.md_bg_color = self.controller.config.ANNOTATION_INCORRECT_COLOR
            self.validate_ambiguous_button.md_bg_color = self.controller.config.ANNOTATION_AMBIGUOUS_COLOR

    def bind_events(self):
        self.validation_confidence_dropdown.on_dismiss = self.on_dropdown_closed

    def on_dropdown_closed(self, *args):
        self.dropdown_visible = False
        print(f"Dropdown Open: {self.dropdown_visible}")
