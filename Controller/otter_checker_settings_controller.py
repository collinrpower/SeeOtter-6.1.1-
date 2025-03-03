from Config.otter_checker_config import OtterCheckerConfig
from Config.see_otter_config import SeeOtterConfig
from Controller.settings_controller import SettingsController


class OtterCheckerSettingsController(SettingsController):

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(config=OtterCheckerConfig.instance())
        return cls._instance
