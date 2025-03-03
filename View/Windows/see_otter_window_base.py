from abc import abstractmethod

from kivymd.app import MDApp
from Config.otter_checker_config import OtterCheckerConfig


class SeeOtterWindowBase(MDApp):

    controller = None

    survey_manager_screen = None
    otter_checker_screen = None
    settings_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_theme()
        self.init_window_settings()

    def init_theme(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = OtterCheckerConfig.instance().ACCENT_COLOR

    @abstractmethod
    def init_window_settings(self):
        pass

    @abstractmethod
    def bind_events(self):
        pass
