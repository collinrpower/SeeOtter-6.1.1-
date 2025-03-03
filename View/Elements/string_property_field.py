from kivymd.uix.textfield import MDTextField

from View.Elements.property_field_base import PropertyFieldBase


class StringPropertyField(PropertyFieldBase):

    text_field_width = 150

    def __init__(self, title, obj, property_name, **kwargs):
        super().__init__(title, obj, property_name, **kwargs)
        self.text_field = MDTextField(size_hint_x=None, width=self.text_field_width)

    def get_content(self):
        return self.text_field

    def set_value(self, value):
        self.text_field.text = str(value)

    def get_value(self):
        return self.text_field.text
