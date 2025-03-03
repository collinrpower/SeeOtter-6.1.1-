from kivy.uix.label import Label
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDRectangleFlatIconButton
from kivymd.uix.gridlayout import MDGridLayout
from Config.otter_checker_config import OtterCheckerConfig
from Controller.image_filter_controller_interface import ImageFilterControllerInterface
from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.slider_label import SliderLabel
from View.Elements.stack_card import StackCard
from View.Elements.toggle_label import ToggleLabel


class FilterSettingsCard(StackCard):

    def __init__(self, filter_controller: ImageFilterControllerInterface, open_filter_drawer_callback, **kwargs):
        super().__init__("Filters", **kwargs)
        self.controller = filter_controller
        self.open_filter_drawer_button = MDRectangleFlatIconButton(text="More", icon="filter-outline",
                                                                   on_press=open_filter_drawer_callback)
        self.size_hint_y = None
        self.height = 310
        self.build()
        self.controller.bind(settings_changed=self.value_changed)

    def build(self):

        min_confidence_slider = SliderLabel(text="Min Confidence",
                                            prop=self.controller.confidence_cutoff)
        min_confidence_slider.slider.bind(value=self.controller.setter('confidence_cutoff'))

        show_images_with_no_prediction_toggle = ToggleLabel(text="Show Images With No Predictions",
                                                            default=self.controller.show_images_with_no_predictions)
        show_images_with_no_prediction_toggle.checkbox.bind(
            active=self.controller.setter('show_images_with_no_predictions'))

        show_unvalidated_validations = ToggleLabel(text="Unvalidated Annotations",
                                                   text_color=OtterCheckerConfig.instance().ANNOTATION_UNVALIDATED_COLOR,
                                                   default=self.controller.show_unvalidated_validations)
        show_unvalidated_validations.checkbox.bind(active=self.controller.setter('show_unvalidated_validations'))

        show_correct_validations_toggle = ToggleLabel(text="Correct Annotations",
                                                      text_color=OtterCheckerConfig.instance().ANNOTATION_CORRECT_COLOR,
                                                      default=self.controller.show_correct_validations)
        show_correct_validations_toggle.checkbox.bind(active=self.controller.setter('show_correct_validations'))

        show_incorrect_validations = ToggleLabel(text="Incorrect Annotations",
                                                 text_color=OtterCheckerConfig.instance().ANNOTATION_INCORRECT_COLOR,
                                                 default=self.controller.show_incorrect_validations)
        show_incorrect_validations.checkbox.bind(active=self.controller.setter('show_incorrect_validations'))

        show_ambiguous_validations = ToggleLabel(text="Ambiguous Annotations",
                                                 text_color=OtterCheckerConfig.instance().ANNOTATION_AMBIGUOUS_COLOR,
                                                 default=self.controller.show_ambiguous_validations)
        show_ambiguous_validations.checkbox.bind(active=self.controller.setter('show_ambiguous_validations'))

        button_layout = MDGridLayout(orientation="lr-tb", cols=2, size_hint=(1, None), height=60, spacing=100)
        self.apply_button = MDFillRoundFlatButton(text="Apply", on_press=self.apply_button_pressed)
        self.apply_button.disabled = True
        button_layout.add_widget(Label(size_hint=(None, None), width=80, height=35))
        button_layout.add_widget(self.apply_button)

        self.add(show_images_with_no_prediction_toggle)
        self.add(min_confidence_slider)
        self.add(show_unvalidated_validations)
        self.add(show_correct_validations_toggle)
        self.add(show_incorrect_validations)
        self.add(show_ambiguous_validations)
        self.add(button_layout)

    def apply_button_pressed(self, instance):
        self.controller.apply_filter()
        self.controller.settings_changed = False
        self.apply_button.disabled = True

    def value_changed(self, instance, value):
        self.apply_button.disabled = False
        self.apply_button.md_bg_color = [.1, .90, .1, 1]
