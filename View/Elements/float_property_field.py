from kivymd.uix.textfield import MDTextFieldRect

from View.Elements.property_field_base import PropertyFieldBase


class FloatPropertyField(PropertyFieldBase):

    def __init__(self, title, obj, property_name, **kwargs):
        super().__init__(title, obj, property_name, **kwargs)

    def get_content(self):
        self.number_box = MDTextFieldRect(size_hint_x=None, width=100,
                                          input_type="number", input_filter="float")
        self.number_box.bind(text=self.validate)
        return self.number_box

    def set_value(self, value):
        self.number_box.text = str(value)

    def get_value(self):
        return self.number_box.text
