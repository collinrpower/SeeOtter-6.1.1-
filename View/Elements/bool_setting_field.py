from kivy.properties import BooleanProperty
from kivymd.uix.selectioncontrol import MDCheckbox
from View.Elements.setting_field_base import SettingFieldBase


class BoolSettingField(SettingFieldBase):

    def __init__(self, title, property_name, **kwargs):
        super().__init__(title, property_name, **kwargs)

    def get_content(self):
        self.checkbox = MDCheckbox(size_hint=(None, None), height=self.height, width=30)
        return self.checkbox

    def get_value(self):
        return self.checkbox.active

    def set_value(self, value):
        self.checkbox.active = value

    def bind_settings_changed(self):
        self.checkbox.bind(active=self.on_setting_changed)

    def validate(self, *args, **kwargs):
        pass
