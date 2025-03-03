from abc import abstractmethod
from typing import List
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from Config.otter_checker_config import OtterCheckerConfig
from Config.serializable_config_base import SerializableConfigBase
from View.Elements.setting_field_interface import SettingFieldInterface


class SettingsController(EventDispatcher):

    settings_changed = BooleanProperty(defaultvalue=False)

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: SerializableConfigBase = config
        self.setting_fields: List[SettingFieldInterface] = []

    @classmethod
    @abstractmethod
    def get_instance(cls):
        pass

    @property
    def default_config(self):
        return self.config.get_default_config()

    def apply_changes_to_config(self, *args, **kwargs):
        for field in self.setting_fields:
            field.update_config()
        self.config.save()
        self.settings_changed = False

    def revert_changes(self, *args, **kwargs):
        for field in self.setting_fields:
            field.load_config_value()
        self.config.save()
        self.settings_changed = False

    def reset_to_default(self, *args, **kwargs):
        self.config.reset_to_default()
        self.config = self.config.instance()
        self.load_from_config()

    def load_from_config(self):
        for field in self.setting_fields:
            try:
                field.load_config_value()
            except Exception as ex:
                print("Error loading config field")
        self.config.save()
        self.settings_changed = False

    def register(self, settings_field):
        self.setting_fields.append(settings_field)

    def get_config_value(self, property_name):
        return getattr(self.config, property_name)

    def get_default_config_value(self, property_name):
        return getattr(self.default_config, property_name)

    def set_config_value(self, property_name, value):
        return setattr(self.config, property_name, value)
