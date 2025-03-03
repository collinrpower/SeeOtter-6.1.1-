from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar

from Controller.see_otter_controller import SeeOtterController
from Controller.see_otter_controller_base import SeeOtterControllerBase, SeeOtterState
from SurveyEntities.survey import Survey
from Utilities.tqdm_plus import TqdmPlus
from View.Elements.property_row import PropertyRow
from View.Elements.stack_card import StackCard
from View.Elements.wide_icon_button import WideIconButton


class ProcessingCard(StackCard):

    def __init__(self, controller: SeeOtterController, title, **kwargs):
        super().__init__(title, **kwargs)
        self.height = 225
        self.controller = controller
        self.build()
        self.update_fields()
        self.bind_events()

    def build(self):
        button_container = GridLayout(cols=2, spacing=20, size_hint_y=None, height=40, padding=[0, 20])
        self.start_processing_button = WideIconButton(callback=self.processing_button_pressed, icon="play",
                                                      tooltip="Start Processing", md_bg_color=(.05, .7, .05, 1),
                                                      pos_hint={"center_x": .5, "center_y": .5})
        self.stop_processing_button = WideIconButton(callback=self.stop_processing_button_pressed, icon="stop",
                                                     tooltip="Stop Processing", md_bg_color=(.8, .1, .1, 1),
                                                     pos_hint={"center_x": .5, "center_y": .5})
        self.current_state = PropertyRow("Current State")
        self.current_command = PropertyRow("Current Command")
        self.processing_progress_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None,
                                                 height=50, halign="left")
        self.processing_time_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None,
                                                 height=50, halign="right")
        self.processing_progress_bar = MDProgressBar(color=(.2, .8, .2, 1), size_hint_y=None, height=10)

        button_container.add_widget(self.start_processing_button)
        button_container.add_widget(self.stop_processing_button)

        process_info_layout = RelativeLayout(size_hint_y=None, height=40)
        process_info_layout.add_widget(self.processing_progress_label)
        process_info_layout.add_widget(self.processing_time_label)

        self.add(self.current_state)
        self.add(self.current_command)
        self.add(button_container)
        self.add(MDLabel(size_hint_y=None, height=20))
        self.add(process_info_layout)
        self.add(self.processing_progress_bar)
        self.add(MDLabel(size_hint_y=None, height=5))

    def clear_fields(self):
        self.current_state.value = ""
        self.current_command.value = "N/A"
        self.processing_progress_label.value = ""
        self.current_state.value = self.controller.state.name
        self.processing_progress_bar.value = 0

    def set_fields(self, survey: Survey):
        self.current_state.value = self.controller.state.name
        self.current_command.value = self.controller.commands.current_command_name
        if self.controller.state == SeeOtterState.RUNNING_IMAGE_DETECTION:
            self.stop_processing_button.disabled = False
            self.start_processing_button.disabled = True
        else:
            self.stop_processing_button.disabled = True
            self.start_processing_button.disabled = False

    def processing_button_pressed(self, *args):
        self.start_processing_button.disabled = True
        self.controller.commands.run_processing()

    def stop_processing_button_pressed(self, *args):
        self.stop_processing_button.disabled = True
        self.controller.set_snackbar_message("Stopping processing")
        self.controller.commands.raise_exit_flag()

    def update_command_progress(self, *args, **kwargs):
        command_progress: TqdmPlus = self.controller.commands.command_progress
        if command_progress:
            self.processing_progress_label.text = str(command_progress)
            self.processing_time_label.text = command_progress.time_rate_str
            self.processing_progress_bar.value = command_progress.progress

    def update_fields(self, *args, **kwargs):
        survey = self.controller.survey
        if survey and isinstance(self.controller.survey, Survey):
            self.set_fields(survey)
        else:
            self.clear_fields()

    def bind_events(self):
        self.controller.bind(survey=self.update_fields)
        self.controller.bind(state=self.update_fields)
        self.controller.commands.bind(current_command_name=self.update_fields)
        self.controller.commands.bind(command_progress=self.update_command_progress)
