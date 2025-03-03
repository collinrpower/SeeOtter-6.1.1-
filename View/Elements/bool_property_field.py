from kivymd.uix.selectioncontrol import MDCheckbox

from View.Elements.property_field_base import PropertyFieldBase


class BoolPropertyField(PropertyFieldBase):

    def __init__(self, title, obj, property_name, **kwargs):
        super().__init__(title, obj, property_name, **kwargs)
        self.checkbox = MDCheckbox()

    def get_content(self):
        return self.checkbox

    def set_value(self, value):
        self.checkbox.active = value

    def get_value(self):
        return self.checkbox.active
