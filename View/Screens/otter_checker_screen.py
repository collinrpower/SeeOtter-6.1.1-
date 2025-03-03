import os.path
from typing import List
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from Controller.see_otter_controller import SeeOtterController
from Controller.see_otter_controller_base import SeeOtterControllerBase, OTTER_CHECKER_MODE
from SurveyEntities.image_tag import ImageTag
from SurveyEntities.object_prediction_data import ValidationState
from SurveyEntities.survey_image import SurveyImage
from Utilities.kivy_utilities import switch_scene
from View.Elements.image_tag_chip import ImageTagChip
from View.Elements.save_button import SaveButton
from View.Elements.toggle_gridlines_button import ToggleGridlinesButton
from View.Popups.program_status_popup import ProgramStatusPopup
from View.Popups.prompt_validator_name_popup import PromptValidatorNamePopup
from View.Widgets.draw_annotation_panel import DrawAnnotationPanel
from View.Widgets.image_tag_chip_card import ImageTagChipCard
from View.Elements.rounded_card import RoundedCard
from View.Elements.transparent_icon_button import TransparentIconButton
from View.Elements.wide_icon_button import WideIconButton
from View.Widgets.annotation_image import AnnotationImage
from View.Widgets.current_image_info_header import CurrentImageInfoHeader
from View.Widgets.filter_settings_card import FilterSettingsCard
from View.Widgets.image_info_card import ImageInfoCard
from View.Widgets.prediction_info_card import PredictionInfoCard
from View.Widgets.validation_buttons_card import ValidationButtonsCard
from View.Screens.survey_screen_base import SurveyScreenBase
from config import KeyBinding

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'


class BoxStencil(BoxLayout, StencilView):
    pass


class ContentNavigationDrawer(MDBoxLayout):
    pass


class OtterCheckerScreen(SurveyScreenBase):
    # UI Elements
    tags_card = None
    zoom_label = None
    toggle_grid_button = None
    validation_buttons = None
    confidence_value_label = None

    # Popups
    prompt_validator_popup = None
    confirm_close_popup = None
    program_status_popup = None

    # Panels
    navigation_panel = None
    image_overlay_control_panel = None

    def __init__(self, controller: SeeOtterController, survey_images: List[SurveyImage] = None, **kwargs):
        super().__init__(**kwargs)
        # self.init_window_settings()
        self.survey_images = survey_images
        self.controller: SeeOtterController = controller
        self.image_panel = AnnotationImage(controller)
        self.left_panel = self.build_left_panel()
        self.top_button_panel = self.build_top_button_panel()
        self.right_panel = self.build_right_panel()
        self.init_popups()
        self.bind_events()
        self.build()
        self.unbind_keypress()
        self.load_splash_screen()

    def load_splash_screen(self):
        self.image_panel.fit_image()
        self.on_splash_screen_loaded()

    def on_splash_screen_loaded(self, *args):
        print("Splash screen loaded")
        self.prompt_validator_name()
        if self.controller and len(self.controller.images) > 0:
            self.update_current_image()

    def prompt_validator_name(self):
        config = self.controller.config
        if config.VALIDATOR_MODE and config.VALIDATOR_NAME is None:
            self.prompt_validator_popup.open()

    def update_current_image(self, *args):
        self.controller.current_image = self.controller.images[0]

    def build(self):
        print("Building Main Window")
        layout = BoxLayout(orientation="horizontal")
        self.image_overlay_control_panel = self.build_image_overlay_control_panel()
        layout.add_widget(self.left_panel)
        layout.add_widget(self.right_panel)
        self.add_widget(layout)
        self.add_widget(self.image_overlay_control_panel)

    def build_right_panel(self):
        right_panel = BoxLayout(orientation="vertical")
        right_panel.add_widget(self.top_button_panel)
        stencil_box = BoxStencil()
        stencil_box.add_widget(self.image_panel)
        right_panel.add_widget(stencil_box)
        return right_panel

    def build_left_panel(self):
        left_panel = MDBoxLayout(orientation="vertical", size_hint=(None, 1.0), spacing=10, padding=10,
                                 width=self.controller.config.LEFT_PANEL_WIDTH)
        self.tags_card = self.build_tags_card()

        self.zoom_label = MDLabel(text="Zoom: 1", size_hint=(1, None), height=25)
        self.toggle_grid_button = ToggleGridlinesButton(controller=self.controller)
        center_image_button = TransparentIconButton(callback=self.image_panel.stretch_image, icon="fullscreen",
                                                    tooltip="Center Image", size_hint_x=None, width=60)
        focus_annotation_button = TransparentIconButton(callback=self.image_panel.pan_to_selected_annotation,
                                                        icon="image-filter-center-focus-strong",
                                                        tooltip="Pan to selected annotation",
                                                        size_hint_x=None, width=60)
        bottom_panel = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=35)
        bottom_panel.add_widget(self.zoom_label)
        bottom_panel.add_widget(self.toggle_grid_button)
        bottom_panel.add_widget(center_image_button)
        bottom_panel.add_widget(focus_annotation_button)
        left_panel.add_widget(FilterSettingsCard(self.controller.filter_controller,
                                                 lambda x: self.navigation_drawer.set_state("open")))
        left_panel.add_widget(ImageInfoCard(self.controller))
        left_panel.add_widget(PredictionInfoCard(self.controller))
        left_panel.add_widget(self.tags_card)
        left_panel.add_widget(bottom_panel)
        return left_panel

    def build_image_overlay_control_panel(self):
        image_overlay_control_panel = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(None, None),
                                                   width=200, height=100)
        button_panel = MDBoxLayout(orientation="horizontal")
        image_overlay_control_panel.add_widget(button_panel)

        return image_overlay_control_panel

    def build_top_button_panel(self):
        button_panel = MDBoxLayout(orientation="horizontal", spacing=15, size_hint=(1, None), height=65)
        switch_to_survey_screen_button = TransparentIconButton(callback=self.switch_to_survey_manager_screen,
                                                               icon="home", tooltip="Settings", size_hint_x=None,
                                                               width=60, md_bg_color=(.05, .4, .7, 1),
                                                               text_color=(1, 0, 0, 1))

        self.navigation_panel = self.build_navigation_panel()

        self.validation_buttons = ValidationButtonsCard(controller=self.controller)

        save_button = SaveButton(controller=self.controller, callback=self.controller.save,
                                 tooltip="Save", size_hint_x=None, width=60)
        load_button = TransparentIconButton(callback=self.open_select_survey_dialog,
                                            icon="folder",
                                            tooltip="Open", size_hint_x=None, width=60)

        button_panel.add_widget(switch_to_survey_screen_button)
        button_panel.add_widget(DrawAnnotationPanel(controller=self.controller))
        button_panel.add_widget(Label(size_hint=(.05, 1)))
        button_panel.add_widget(self.navigation_panel)
        button_panel.add_widget(Label(size_hint=(.05, 1)))
        button_panel.add_widget(self.validation_buttons)
        button_panel.add_widget(load_button)
        button_panel.add_widget(save_button)
        button_panel.add_widget(Label(size_hint=(None, .8), width=10))

        return button_panel

    def build_navigation_panel(self):
        navigation_panel = RoundedCard(orientation="horizontal", size_hint=(None, 1), width="720dp", padding=10)

        layout = MDBoxLayout(orientation="horizontal", spacing=25, size_hint=(1, None), height=65,
                             pos_hint={"center_x": .5, "center_y": .5})
        previous_image_button = WideIconButton(callback=self.controller.previous_image, icon="skip-backward",
                                               tooltip="Previous Image")
        layout.add_widget(previous_image_button)
        previous_prediction_button = WideIconButton(callback=self.controller.previous_prediction, icon="step-backward",
                                                    tooltip="Previous Prediction")
        layout.add_widget(previous_prediction_button)
        layout.add_widget(CurrentImageInfoHeader(self.controller, size_hint=(.5, 1)))
        next_prediction_button = WideIconButton(callback=self.controller.next_prediction, icon="step-forward",
                                                tooltip="Next Prediction")
        layout.add_widget(next_prediction_button)
        next_image_button = WideIconButton(callback=self.controller.next_image, icon="skip-forward",
                                           tooltip="Next Image")
        layout.add_widget(next_image_button)
        navigation_panel.add_widget(layout)
        return navigation_panel

    def build_tags_card(self):
        card = ImageTagChipCard([
            ImageTagChip(ImageTag(name=tag)) for tag in self.controller.config.IMAGE_TAGS],
            on_tag_pressed=self.controller.tag_selected)
        return card

    def init_popups(self):
        self.prompt_validator_popup = PromptValidatorNamePopup(controller=self.controller)
        self.program_status_popup = ProgramStatusPopup(controller=self.controller)

    def handle_key_down(self, keyboard, keycode, text, modifiers, *args):
        if keycode == KeyBinding.HIDE_ANNOTATIONS:
            self.image_panel.annotations_visible = False
        if keycode == KeyBinding.EDIT_ANNOTATIONS:
            self.image_panel.mode = OTTER_CHECKER_MODE.EDIT_ANNOTATION
        if keycode == KeyBinding.DELETE_PREDICTION:
            self.image_panel.remove_selected_prediction()
        if keycode == KeyBinding.TOGGLE_DRAW_MODE:
            self.controller.toggle_draw_mode()
        if keycode == KeyBinding.PREVIOUS_PREDICTION:
            self.controller.previous_prediction()
        if keycode == KeyBinding.NEXT_PREDICTION:
            self.controller.next_prediction()
        if keycode == KeyBinding.NEXT_IMAGE:
            self.controller.next_image()
        if keycode == KeyBinding.PREVIOUS_IMAGE:
            self.controller.previous_image()
        if keycode == KeyBinding.PAN_TO_SELECTED_PREDICTION:
            self.image_panel.pan_to_selected_annotation()
        if keycode == KeyBinding.VALIDATE_CORRECT:
            self.controller.set_current_image_validation_state(ValidationState.CORRECT)
        if keycode == KeyBinding.VALIDATE_INCORRECT:
            self.controller.set_current_image_validation_state(ValidationState.INCORRECT)
        if keycode == KeyBinding.VALIDATE_AMBIGUOUS:
            self.validation_buttons.on_ambiguous_validation_pressed()

    def handle_key_up(self, keyboard, keycode, text, *args):
        if keycode == KeyBinding.HIDE_ANNOTATIONS:
            self.image_panel.annotations_visible = True
        if keycode == KeyBinding.EDIT_ANNOTATIONS:
            self.image_panel.mode = OTTER_CHECKER_MODE.DEFAULT

    def on_mode_changed(self, *args):
        if self.controller.default_mode:
            self.left_panel.disabled = False
            self.navigation_panel.disabled = False
            self.validation_buttons.disabled = False
        if self.controller.draw_mode:
            self.left_panel.disabled = True
            self.navigation_panel.disabled = True
            self.validation_buttons.disabled = True
        if self.controller.edit_mode:
            pass

    def switch_to_survey_manager_screen(self, *args, **kwargs):
        switch_scene(obj=self, scene="survey_manager", direction="right")

    def unbind_keypress(self, *args):
        Window.unbind(on_key_down=self.handle_key_down)
        Window.unbind(on_key_up=self.handle_key_up)

    def bind_keypress(self, *args):
        Window.bind(on_key_down=self.handle_key_down)
        Window.bind(on_key_up=self.handle_key_up)

    def bind_events(self):
        self.image_panel.event.bind(on_zoom_level_changed=self.update_zoom_label)
        self.controller.bind(current_image=self.tags_card.update_tag_state)
        self.controller.bind(mode=self.on_mode_changed)
        self.controller.bind(survey=self.on_survey_changed)

    def on_enter(self, *args, **kwargs):
        self.bind_keypress()
        if self.image_panel.current_image_is_background:
            self.image_panel.stretch_image()

    def on_leave(self, *args):
        self.unbind_keypress()

    def update_zoom_label(self, *args):
        self.zoom_label.text = f"Zoom: {self.image_panel.zoom_level:.3f}x"

    def on_value(self, instance, brightness):
        self.confidence_value_label.text = f"% {brightness:.2f}"

    def on_survey_changed(self, *args):
        print(f"Survey changed: {self.controller.survey}")
