from functools import partial
import kivy
from kivy import Config
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
import version
from Controller.see_otter_controller import SeeOtterController
from Utilities.kivy_utilities import switch_scene
from Utilities.utilities import PromptUserNotification
from View.Dialogs.yes_no_dialog import YesNoDialog
from View.Popups.confirm_close_without_saving_popup import ConfirmCloseWithoutSavingPopup
from View.Screens.settings_screen import SettingsScreen
from View.Screens.otter_checker_screen import OtterCheckerScreen
from View.Screens.survey_manager_screen import SurveyManagerScreen
from View.Widgets.custom_snackbar import CustomSnackbar
from View.Windows.see_otter_window_base import SeeOtterWindowBase
kivy.require('1.9.0')
from kivy.uix.screenmanager import ScreenManager


resolutions = [(1920, 1080), (3440, 1440)]


class SeeOtterWindow(SeeOtterWindowBase):

    snackbar = None
    scene_manager = None

    def __init__(self, survey=None, startup_screen="survey_manager", **kwargs):
        super().__init__(**kwargs)
        self.controller = SeeOtterController(window=self, survey=survey)
        self.confirm_close_popup = ConfirmCloseWithoutSavingPopup(save_action=self.save_and_exit,
                                                                  continue_without_saving_action=Window.close)
        self.snackbar = CustomSnackbar(text=self.controller.snackbar_message, snackbar_x="10dp", snackbar_y="10dp",
                                       size_hint_x=(Window.width - (dp(10) * 2)) / Window.width, icon="information",
                                       duration=6)
        self.startup_screen = startup_screen
        self.bind_events()

    def init_window_settings(self):
        self.title = f'SeeOtter ({version.version})'
        Window.size = resolutions[0]
        Window.fullscreen = False
        Window.bind(on_request_close=self.on_window_close)
        #Window.bind(focus=)
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        Config.set('graphics', 'resizable', '1')
        Config.set('graphics', 'multisamples', '0')
        Config.write()

    def bind_events(self):
        self.controller.bind(snackbar_message=self.update_snackbar)
        PromptUserNotification.callback = self.on_user_prompt

    def on_user_prompt(self, message):
        print("****On user prompt")
        Clock.schedule_once(partial(self.open_user_prompt_dialog, message), -1)

    @staticmethod
    def open_user_prompt_dialog(message, *args, **kwargs):
        print("Opening yes/no dialog")
        YesNoDialog(message=message,
                    yes_action=partial(PromptUserNotification.respond, True),
                    no_action=partial(PromptUserNotification.respond, False)
                    ).open()

    def build(self):

        self.scene_manager = ScreenManager()

        self.survey_manager_screen = SurveyManagerScreen(controller=self.controller, name="survey_manager")
        self.otter_checker_screen = OtterCheckerScreen(controller=self.controller, name="otter_checker")
        self.settings_screen = SettingsScreen(controller=self.controller, name="settings")

        self.scene_manager.add_widget(self.survey_manager_screen)
        self.scene_manager.add_widget(self.otter_checker_screen)
        self.scene_manager.add_widget(self.settings_screen)

        return self.scene_manager

    def update_snackbar(self, *args, **kwargs):
        message = self.controller.snackbar_message
        if message:
            print(f"Snackbar message: {message}")
        if message != "":
            if message.startswith("Error"):
                self.snackbar.icon = "alert-box"
                self.snackbar.icon_color = (.75, .05, .05, 1)
                self.snackbar.duration = 8
            elif message.startswith("Warning"):
                self.snackbar.icon = "alert"
                self.snackbar.icon_color = (.75, .75, .05, 1)
                self.snackbar.duration = 8
            else:
                self.snackbar.icon = "information"
                self.snackbar.duration = 4
                self.snackbar.icon_color = (.05, .4, .7, 1)
            self.snackbar.text = message
            self.snackbar.open()

    def on_start(self):
        print("On SeeOtter window start")
        switch_scene(obj=self.survey_manager_screen, scene=self.startup_screen, duration=0)

    def on_window_close(self, *args):
        if self.controller.has_unsaved_changes:
            print("Unsaved changes")
            self.confirm_close_popup.open()
            return True

    def save_and_exit(self, *args):
        self.controller.survey.save()
        Window.close()
