from kivy.core.window import Window
from kivy.uix.label import Label
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from Controller.see_otter_controller import SeeOtterController
from Controller.see_otter_controller_base import SeeOtterState
from Utilities.kivy_utilities import switch_scene
from View.Elements.save_button import SaveButton
from View.Elements.transparent_icon_button import TransparentIconButton
from View.Popups.clone_filtered_survey_popup import CloneFilteredSurveyPopup
from View.Popups.new_survey_popup import NewSurveyPopup
from View.Widgets.camera_system_card import CameraSystemCard
from View.Widgets.inclinometer_card import InclinometerCard
from View.Widgets.predictions_overview_info_card import PredictionsOverviewInfoCard
from View.Widgets.processing_status_card import ProcessingCard
from View.Widgets.survey_actions_card import SurveyActionsCard
from View.Widgets.survey_info_card import SurveyInfoCard
from View.Screens.survey_screen_base import SurveyScreenBase
from View.Widgets.transects_card import TransectsCard
from config import PANEL_SPACING, PANEL_PADDING


class SurveyManagerScreen(SurveyScreenBase):
    processing_card = None
    survey_actions_card = None
    survey_info_card = None
    predictions_overview_card = None
    inclinometer_card = None
    camera_system_card = None
    transects_card = None
    debug_colors = False
    cards = []
    new_survey_blue = (.05, .4, .7, 1)

    def __init__(self, controller: SeeOtterController, **kwargs):
        super().__init__(**kwargs)
        self.controller: SeeOtterController = controller
        self.build_cards()
        self.build()
        self.bind_events()
        self.on_survey_changed()

    def build(self):
        layout = GridLayout(rows=2, spacing=PANEL_SPACING * 2)

        self.top_bar = self.build_top_panel()
        self.columns = MDBoxLayout(orientation="horizontal", spacing=PANEL_SPACING, padding=[PANEL_PADDING, 0])

        self.left_panel = self.build_left_panel()
        self.middle_panel = self.build_middle_panel()
        self.right_panel = self.build_right_panel()

        self.columns.add_widget(self.left_panel)
        self.columns.add_widget(self.middle_panel)
        self.columns.add_widget(self.right_panel)

        if self.debug_colors:
            self.apply_debug_colors()

        layout.add_widget(self.top_bar)
        layout.add_widget(self.columns)

        self.add_widget(layout)

    def build_top_panel(self):
        layout = MDBoxLayout(orientation="horizontal", spacing=25, md_bg_color=(1, 1, 1, .1),
                             padding=[PANEL_PADDING + 12], size_hint=(1, None),
                             height=65, pos_hint={"center_x": .5, "center_y": .5})
        self.new_survey_button = TransparentIconButton(callback=self.open_new_survey_popup, icon="plus",
                                                       tooltip="New Survey", md_bg_color=self.new_survey_blue)
        self.load_button = TransparentIconButton(callback=self.open_select_survey_dialog, icon="folder",
                                                 tooltip="Open", size_hint_x=None, width=60)
        self.save_button = SaveButton(controller=self.controller, callback=self.controller.save, tooltip="Save")
        self.refresh_button = TransparentIconButton(callback=self.refresh_ui, icon="refresh",
                                                    tooltip="Refresh UI", size_hint_x=None, width=60)
        self.generate_results_button = TransparentIconButton(callback=self.controller.commands.generate_results,
                                                             tooltip="Generate Results", icon="file-chart-outline")
        self.open_user_guide_button = TransparentIconButton(callback=self.controller.open_user_guide,
                                                            tooltip="Open User Guide", icon="help-circle")
        self.open_otter_checker_button = MDFillRoundFlatButton(text="Open OtterChecker9000",
                                                               pos_hint={"center_x": .5, "center_y": .5},
                                                               on_press=self.switch_to_otter_checker_screen)
        self.open_settings_button = TransparentIconButton(text="Open Settings", icon="wrench",
                                                          pos_hint={"center_x": .5, "center_y": .5}, tooltip="Settings",
                                                          callback=self.switch_to_settings_screen)

        layout.add_widget(self.new_survey_button)
        layout.add_widget(self.load_button)
        layout.add_widget(self.save_button)
        layout.add_widget(self.refresh_button)
        layout.add_widget(self.generate_results_button)
        layout.add_widget(self.open_user_guide_button)
        layout.add_widget(self.open_settings_button)
        layout.add_widget(Label(size_hint_x=None, width=100))
        layout.add_widget(Label(size_hint_x=.6, width=100))
        layout.add_widget(self.open_otter_checker_button)
        return layout

    def build_left_panel(self):
        layout = MDStackLayout(orientation="tb-lr", size_hint_x=.75, spacing=PANEL_SPACING, padding=[PANEL_PADDING, 0])
        layout.add_widget(self.processing_card)
        layout.add_widget(self.survey_actions_card)
        return layout

    def build_middle_panel(self):
        layout = MDStackLayout(orientation="tb-lr", size_hint_x=1, spacing=PANEL_SPACING, padding=[PANEL_PADDING, 0])
        layout.add_widget(self.survey_info_card)
        layout.add_widget(self.camera_system_card)
        return layout

    def build_right_panel(self):
        layout = MDStackLayout(orientation="tb-lr", size_hint_x=.75, spacing=PANEL_SPACING, padding=[PANEL_PADDING, 0])
        layout.add_widget(self.predictions_overview_card)
        layout.add_widget(self.transects_card)
        layout.add_widget(self.inclinometer_card)
        return layout

    def build_cards(self):
        self.survey_info_card = SurveyInfoCard(title="Survey Overview", controller=self.controller)
        self.processing_card = ProcessingCard(title="Processing", controller=self.controller)
        self.survey_actions_card = SurveyActionsCard(title="Actions", controller=self.controller)
        self.predictions_overview_card = PredictionsOverviewInfoCard(title="Predictions and Validations",
                                                                     controller=self.controller)
        self.transects_card = TransectsCard(title="Transects", controller=self.controller)
        self.camera_system_card = CameraSystemCard(title="Camera System", controller=self.controller)
        self.inclinometer_card = InclinometerCard(title="Inclinometer", controller=self.controller)

        self.cards = [self.survey_info_card, self.processing_card, self.survey_actions_card,
                      self.predictions_overview_card, self.transects_card, self.camera_system_card,
                      self.inclinometer_card]

    def open_new_survey_popup(self, *args, **kwargs):
        popup = NewSurveyPopup(command_controller=self.controller.commands, controller=self.controller)
        popup.open()

    def switch_to_otter_checker_screen(self, *args, **kwargs):
        switch_scene(obj=self, scene="otter_checker", direction="left")

    def switch_to_settings_screen(self, *args, **kwargs):
        switch_scene(obj=self, scene="settings", direction="right")

    def refresh_ui(self, *args):
        for card in self.cards:
            card.update_fields()
        if args:
            self.controller.set_snackbar_message("Refreshed UI")

    def apply_debug_colors(self):
        red, green, blue = (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)
        self.top_bar.md_bg_color = red
        self.left_panel.md_bg_color = green
        self.middle_panel.md_bg_color = green
        self.right_panel.md_bg_color = green

    def on_start(self):
        print("SeeOtter Starting")

    def on_pre_enter(self, *args):
        self.refresh_ui()

    def on_state_changed(self, *args, **kwargs):
        print(f"State changed: {self.controller.state.name}")
        state = self.controller.state
        disable_on_command_running = [self.new_survey_button, self.save_button, self.load_button, self.save_button,
                                      self.open_otter_checker_button, self.refresh_button, self.open_settings_button,
                                      self.generate_results_button]
        if state == SeeOtterState.SURVEY_LOADED:
            for button in disable_on_command_running:
                button.disabled = False
            self.new_survey_button.md_bg_color = self.new_survey_blue
            self.open_otter_checker_button.md_bg_color = self.open_otter_checker_button.md_bg_color
        if state not in (SeeOtterState.SURVEY_LOADED, SeeOtterState.NO_SURVEY_LOADED):
            for button in disable_on_command_running:
                button.disabled = True
        if state == SeeOtterState.NO_SURVEY_LOADED:
            self.load_button.disabled = False
            self.open_otter_checker_button.disabled = False
            self.new_survey_button.disabled = False

    def on_survey_changed(self, *args, **kwargs):
        disable_on_no_survey = self.cards + [self.generate_results_button, self.refresh_button]
        for widget in disable_on_no_survey:
            widget.disabled = self.controller.survey is None

    def handle_key_down(self):
        pass

    def handle_key_up(self):
        pass

    def bind_events(self):
        self.controller.bind(state=self.on_state_changed)
        self.controller.bind(survey=self.on_survey_changed)
