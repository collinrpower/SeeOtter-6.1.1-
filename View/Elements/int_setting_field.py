from View.Elements.float_setting_field import FloatSettingField


class IntSettingField(FloatSettingField):

    def __init__(self, title, property_name, tooltip="", **kwargs):
        super().__init__(title, property_name, tooltip=tooltip, **kwargs)

    def get_value(self):
        return int(self.number_box.text)

    def validate(self, *args, **kwargs):
        super().validate()
        if self.error_text != "":
            return
        try:
            value = int(self.number_box.text)
        except:
            self.error_text = "Value must be an integer"
