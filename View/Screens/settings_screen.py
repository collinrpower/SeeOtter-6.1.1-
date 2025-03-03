from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from Controller.otter_checker_settings_controller import OtterCheckerSettingsController
from Controller.see_otter_controller_base import SeeOtterControllerBase
from Controller.see_otter_settings_controller import SeeOtterSettingsController
from Controller.settings_controller import SettingsController
from Utilities.kivy_utilities import switch_scene
from View.Elements.bool_setting_field import BoolSettingField
from View.Elements.float_setting_field import FloatSettingField
from View.Elements.int_setting_field import IntSettingField
from View.Elements.string_setting_field import StringSettingField
from View.Elements.transparent_icon_button import TransparentIconButton
from config import PANEL_SPACING, PANEL_PADDING

Builder.load_string("""
<OtterCheckerSettingsScreen>:
    
""")


class MainHeader(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(theme_text_color="Custom", text_color="orange", **kwargs)
        self.font_style = "H4"
        self.size_hint_y = None
        self.height = 75

    def __draw_shadow__(self, origin, end, context=None):
        pass


class SectionHeader(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_style = "H6"
        self.size_hint_y = None
        self.height = 50

        # self.theme_text_color = "Secondary"

    def __draw_shadow__(self, origin, end, context=None):
        pass


class SettingsLayout(BoxLayout):

    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = PANEL_SPACING
        self.add_widget(MainHeader(text=title))


class SettingsScreen(Screen):
    primary_label_height = 75
    secondary_label_height = 50

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.otter_checker_settings_controller = OtterCheckerSettingsController.get_instance()
        self.see_otter_settings_controller = SeeOtterSettingsController.get_instance()
        self.build()
        self.bind_events()
        self.on_settings_changed()

    def build(self):
        page_layout = GridLayout(cols=3)

        center_panel = BoxLayout(orientation="vertical")
        settings_layout = BoxLayout(orientation="horizontal", pos_hint={"left": 1, "top": 1})

        see_otter_settings = self.build_see_otter_settings_panel()
        otter_checker_settings = self.build_otter_checker_settings_panel()

        settings_layout.add_widget(see_otter_settings)
        settings_layout.add_widget(otter_checker_settings)

        right_panel = BoxLayout(orientation="vertical", size_hint_x=.3)
        switch_to_survey_screen_button = TransparentIconButton(callback=self.switch_to_survey_manager_screen,
                                                               icon="home", tooltip="Settings", size_hint_x=None,
                                                               width=60, md_bg_color=(.05, .4, .7, 1),
                                                               text_color=(1, 0, 0, 1),
                                                               pos_hint={"right": .99, "top": .98})
        right_panel.add_widget(Label(size_hint_y=1))

        bottom_buttons_row = MDBoxLayout(orientation="horizontal", spacing=PANEL_SPACING * 2, padding=PANEL_PADDING,
                                         size_hint_y=None, height=100)

        self.revert_changes_button = MDRaisedButton(text="Revert Changes",
                                                    on_release=self.revert_changes)
        self.reset_to_default_button = MDRaisedButton(text="Reset to Default",
                                                      on_release=self.reset_to_default)
        self.apply_settings_button = MDRaisedButton(text="Apply",
                                                    on_release=self.apply_changes_to_config)
        self.cancel_button = MDRectangleFlatButton(text="Cancel", on_release=self.cancel_button_pressed)
        bottom_buttons_row.add_widget(self.revert_changes_button)
        bottom_buttons_row.add_widget(self.reset_to_default_button)
        bottom_buttons_row.add_widget(MDLabel(size_hint_x=.8))
        bottom_buttons_row.add_widget(self.apply_settings_button)
        bottom_buttons_row.add_widget(self.cancel_button)

        center_panel.add_widget(Label(size_hint_y=None, height=25))
        center_panel.add_widget(settings_layout)
        center_panel.add_widget(bottom_buttons_row)

        scroll_panel = ScrollView(size_hint=(1, 1))
        scroll_panel.add_widget(center_panel)

        page_layout.add_widget(Label(size_hint_x=.3))
        page_layout.add_widget(scroll_panel)
        page_layout.add_widget(right_panel)

        self.add_widget(switch_to_survey_screen_button)
        self.add_widget(page_layout)

    def build_see_otter_settings_panel(self):
        see_otter_settings = SettingsLayout("SeeOtter Settings")
        see_otter_settings.add_widget(SectionHeader(text="Execution"))
        see_otter_settings.add_widget(BoolSettingField(title="Require GPS data for images",
                                                       property_name="REQUIRE_GPS",
                                                       controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(BoolSettingField(title="Fail on missing image exif data",
                                                       property_name="FAIL_ON_MISSING_EXIF_FIELD",
                                                       controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="Min distance for heading calculation",
                                                      property_name="MIN_DISTANCE_FOR_DIRECTION_CALCULATION",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="Max distance for heading calculation",
                                                      property_name="MAX_DISTANCE_FOR_DIRECTION_CALCULATION",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(FloatSettingField(title="Near temporal zone tolerance scale",
                                                        property_name="NEAR_TEMPORAL_ZONE_TOLERANCE",
                                                        controller=self.see_otter_settings_controller,
                                                        min_value=1, max_value=2))

        see_otter_settings.add_widget(SectionHeader(text="Predictions"))
        see_otter_settings.add_widget(IntSettingField(title="Max prediction failure retries", min_value=0,
                                                      max_value=100, property_name="MAX_PREDICTION_RETRIES",
                                                      controller=self.see_otter_settings_controller,
                                                      tooltip="Max number of consecutive failures before predictions "
                                                              "will raise error"))
        see_otter_settings.add_widget(FloatSettingField(title="Prediction min confidence", min_value=0, max_value=1,
                                                        property_name="PREDICTION_CONFIDENCE_CUTOFF",
                                                        controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(BoolSettingField(title="Slice predicted images",
                                                       property_name="SLICE_PREDICTED_IMAGES",
                                                       controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(BoolSettingField(title="Backup survey on predictions complete",
                                                       property_name="BACKUP_SURVEY_ON_PREDICTIONS_COMPLETE",
                                                       controller=self.see_otter_settings_controller))

        see_otter_settings.add_widget(SectionHeader(text="Transects"))
        see_otter_settings.add_widget(IntSettingField(title="Transect lateral tolerance",
                                                      property_name="TRANSECT_LATERAL_TOLERANCE",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="Transect bearing tolerance",
                                                      property_name="TRANSECT_BEARING_TOLERANCE",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="Max off-transect image gap",
                                                      property_name="MAX_OFF_TRANSECT_IMAGE_GAP",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="On-transect min altitude",
                                                      property_name="MIN_ON_TRANSECT_ALTITUDE_FT",
                                                      controller=self.see_otter_settings_controller))
        see_otter_settings.add_widget(IntSettingField(title="On-transect max altitude",
                                                      property_name="MAX_ON_TRANSECT_ALTITUDE_FT",
                                                      controller=self.see_otter_settings_controller))

        see_otter_settings.add_widget(BoxLayout(orientation="vertical", size_hint_y=.8))
        return see_otter_settings

    def build_otter_checker_settings_panel(self):
        otter_checker_settings = SettingsLayout("OtterChecker Settings")
        otter_checker_settings.add_widget(SectionHeader(text="Validation"))
        otter_checker_settings.add_widget(StringSettingField(title="Validator Name", property_name="VALIDATOR_NAME",
                                                             controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Validation Mode", property_name="VALIDATOR_MODE",
                                                           controller=self.otter_checker_settings_controller))

        otter_checker_settings.add_widget(SectionHeader(text="Default Filter Settings"))
        otter_checker_settings.add_widget(FloatSettingField(title="Minimum Confidence", min_value=0, max_value=1,
                                                            property_name="MIN_CONFIDENCE",
                                                            controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Show images with no predictions",
                                                           property_name="SHOW_IMAGES_WITH_NO_PREDICTIONS",
                                                           controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Show correct validations",
                                                           property_name="OTTER_CHECKER_SHOW_UNVALIDATED_VALIDATIONS",
                                                           controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Show correct validations",
                                                           property_name="OTTER_CHECKER_SHOW_CORRECT_VALIDATIONS",
                                                           controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Show incorrect validations",
                                                           property_name="OTTER_CHECKER_SHOW_INCORRECT_VALIDATIONS",
                                                           controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(BoolSettingField(title="Show ambiguous validations",
                                                           property_name="OTTER_CHECKER_SHOW_AMBIGUOUS_VALIDATIONS",
                                                           controller=self.otter_checker_settings_controller))

        otter_checker_settings.add_widget(SectionHeader(text="Behavior"))
        otter_checker_settings.add_widget(FloatSettingField(title="Prediction transition animation time(s)",
                                                            property_name="NEXT_PREDICTION_TRANSITION_TIME",
                                                            controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(FloatSettingField(title="Post validation delay(s)",
                                                            property_name="NEXT_PREDICTION_TRANSITION_TIME",
                                                            controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(FloatSettingField(title="Default prediction zoom level",
                                                            property_name="DEFAULT_ZOOM",
                                                            controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(FloatSettingField(title="Tooltip delay(s)", min_value=0, max_value=4,
                                                            property_name="TOOLTIP_DELAY",
                                                            controller=self.otter_checker_settings_controller))

        otter_checker_settings.add_widget(SectionHeader(text="Grid"))
        otter_checker_settings.add_widget(IntSettingField(title="Grid Rows",
                                                          property_name="GRID_ROWS",
                                                          controller=self.otter_checker_settings_controller))
        otter_checker_settings.add_widget(IntSettingField(title="Grid Columns",
                                                          property_name="GRID_COLUMNS",
                                                          controller=self.otter_checker_settings_controller))

        otter_checker_settings.add_widget(BoxLayout(orientation="vertical", size_hint_y=.8))
        return otter_checker_settings

    def cancel_button_pressed(self, *args):
        self.revert_changes()
        self.switch_to_survey_manager_screen()

    def apply_changes_to_config(self, *args):
        self.otter_checker_settings_controller.apply_changes_to_config()
        self.see_otter_settings_controller.apply_changes_to_config()

    def reset_to_default(self, *args):
        print("Resetting to default")
        self.otter_checker_settings_controller.reset_to_default()
        self.see_otter_settings_controller.reset_to_default()

    def revert_changes(self, *args):
        self.otter_checker_settings_controller.revert_changes()
        self.see_otter_settings_controller.revert_changes()

    def bind_events(self):
        self.otter_checker_settings_controller.bind(settings_changed=self.on_settings_changed)
        self.see_otter_settings_controller.bind(settings_changed=self.on_settings_changed)

    def on_settings_changed(self, *args, **kwargs):
        if self.otter_checker_settings_controller.settings_changed or \
                self.see_otter_settings_controller.settings_changed:
            self.apply_settings_button.disabled = False
            self.revert_changes_button.disabled = False
        else:
            self.apply_settings_button.disabled = True
            self.revert_changes_button.disabled = True

    def on_enter(self, *args):
        pass

    def switch_to_survey_manager_screen(self, *args, **kwargs):
        switch_scene(obj=self, scene="survey_manager", direction="left")
