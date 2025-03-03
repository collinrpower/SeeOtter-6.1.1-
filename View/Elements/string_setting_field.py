from kivymd.uix.textfield import MDTextField

from View.Elements.setting_field_base import SettingFieldBase


class StringSettingField(SettingFieldBase):

    text_field = None
    text_box_width = 200

    def __init__(self, title, property_name, tooltip="", **kwargs):
        super().__init__(title, property_name, tooltip=tooltip, **kwargs)
        self.height = 35

    def get_content(self):
        self.text_field = MDTextField(text="", size_hint_x=None, width=self.text_box_width)
        return self.text_field

    def get_value(self):
        value = self.text_field.text or ""
        return self.text_field.text

    def set_value(self, value):
        value = value or ""
        self.text_field.text = value

    def bind_settings_changed(self):
        self.text_field.bind(text=self.on_setting_changed)

    def validate(self, *args, **kwargs):
        pass