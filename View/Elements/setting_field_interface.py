from abc import abstractmethod

from kivy.properties import StringProperty


class SettingFieldInterface:

    error_text = StringProperty()

    def has_validation_error(self):
        return self.error_text != ""

    @abstractmethod
    def update_config(self):
        pass

    @abstractmethod
    def load_config_value(self):
        pass

    @abstractmethod
    def load_default_config_value(self):
        pass
