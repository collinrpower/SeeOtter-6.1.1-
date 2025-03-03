from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextFieldRect, MDTextField

from View.Elements.setting_field_base import SettingFieldBase


class FloatSettingField(SettingFieldBase):

    number_box = None
    box_width = 100
    min_value = None
    max_value = None

    def __init__(self, title, property_name, min_value=None, max_value=None, tooltip="", **kwargs):
        super().__init__(title, property_name, tooltip=tooltip, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.height = 30

    def get_content(self):

        self.number_box = MDTextFieldRect(size_hint_x=None, width=FloatSettingField.box_width,
                                          input_type="number", input_filter="float")
        self.number_box.bind(text=self.validate)
        return self.number_box

    def get_value(self):
        return float(self.number_box.text)

    def set_value(self, value):
        self.number_box.text = str(value)

    def bind_settings_changed(self):
        self.number_box.bind(text=self.on_setting_changed)

    def on_error_text(self, *args):
        self.error_label.text = self.error_text

    def validate(self, *args, **kwargs):
        text = self.number_box.text
        value = 0.0
        if len(text) == 0:
            self.error_text = "Field Required"
            return
        try:
            value = float(text)
        except Exception:
            self.error_text = f"Invalid entry"
            return
        if self.min_value and value < self.min_value:
            self.error_text = f"Value must be greater than {self.min_value}"
        elif self.max_value and value > self.max_value:
            self.error_text = f"Value must be less than {self.max_value}"
        else:
            self.error_text = ""
