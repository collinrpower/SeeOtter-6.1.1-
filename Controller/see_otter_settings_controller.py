from Config.see_otter_config import SeeOtterConfig
from Controller.settings_controller import SettingsController


class SeeOtterSettingsController(SettingsController):

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(SeeOtterConfig.instance())
        return cls._instance
