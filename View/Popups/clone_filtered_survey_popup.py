from os.path import normpath, join
from pathlib import Path

from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from Config.otter_checker_config import OtterCheckerConfig
from Controller.see_otter_controller_base import SeeOtterControllerBase
from Controller.survey_command_controller import SurveyCommandController
from SurveyEntities.object_prediction_data import ValidationState
from View.Elements.toggle_chip import ToggleChip
from config import PANEL_PADDING, PANEL_SPACING


class CloneFilteredSurveyPopup(Popup):

    chips = []

    def __init__(self, command_controller: SurveyCommandController, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.command_controller = command_controller
        self.controller = controller
        self.title = "Clone Filtered Survey"
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size = (750, 500)
        self.build()
        self.update_cloned_survey_path()
        self.on_chip_pressed()

    def build(self):
        layout = RelativeLayout()
        content_layout = MDBoxLayout(orientation="vertical", pos_hint={"left": 1, "top": 1}, spacing=PANEL_SPACING*2,
                                     padding=PANEL_PADDING)
        chip_stack = MDBoxLayout(orientation="vertical", spacing=5)
        for validation_state in ValidationState:
            color = OtterCheckerConfig.instance().get_validation_color(validation_state)
            chip = ToggleChip(text=validation_state.name, obj=validation_state, selected_color=color)
            chip_stack.add_widget(chip)
            self.chips.append(chip)
            chip.bind(is_selected=self.on_chip_pressed)

        self.cloned_survey_postfix_text_field = MDTextField(text="", hint_text="Cloned Survey Postfix", required=True,
                                                            helper_text="This will be added to the name of the cloned "
                                                                        "survey directory.",
                                                            helper_text_mode="on_focus")
        self.cloned_survey_path_label = MDLabel(size_hint_y=None, height=40)
        self.cloned_survey_postfix_text_field.bind(text=self.update_cloned_survey_path)

        bottom_buttons_row = MDBoxLayout(orientation="horizontal", spacing=PANEL_SPACING * 2, padding=PANEL_PADDING,
                                         pos_hint={"bottom": 1, "right": 1})

        self.run_button = MDRaisedButton(text="Run", on_press=self.run)

        bottom_buttons_row.add_widget(MDLabel(size_hint_x=.8))
        bottom_buttons_row.add_widget(self.run_button)
        bottom_buttons_row.add_widget(MDRectangleFlatButton(text="Cancel", on_press=self.dismiss))
        content_layout.add_widget(MDLabel(text="Create a clone of the current survey containing only the selected "
                                               "validation types, and images containing the selected validation "
                                               "types. A copy of the current survey will be created in the same "
                                               "directory with the given postfix added.",
                                          theme_text_color="Secondary"))
        content_layout.add_widget(chip_stack)
        content_layout.add_widget(self.cloned_survey_postfix_text_field)
        content_layout.add_widget(self.cloned_survey_path_label)
        content_layout.add_widget(Label(size_hint_y=.5))

        layout.add_widget(content_layout)
        layout.add_widget(bottom_buttons_row)

        self.content = layout

    def on_chip_pressed(self, *args):
        self.validate_can_run()

    def update_cloned_survey_path(self, *args):
        survey_dir = self.controller.survey.project_path
        cloned_survey_name = normpath(str(survey_dir) + self.cloned_survey_postfix_text_field.text)
        self.cloned_survey_path_label.text = "Cloned Survey Path: " + cloned_survey_name
        self.validate_can_run()

    def validate_can_run(self):
        for chip in self.chips:
            if chip.is_selected is True:
                if len(self.cloned_survey_postfix_text_field.text) > 0:
                    self.run_button.disabled = False
                    return
        self.run_button.disabled = True

    def run(self, *args):
        validation_types = [chip.obj for chip in self.chips if chip.is_selected]
        cloned_survey_path = str(Path(self.controller.survey.project_path)) + \
                             self.cloned_survey_postfix_text_field.text
        self.command_controller.clone_filtered_survey(cloned_survey_path=cloned_survey_path,
                                                      validation_types=validation_types)
