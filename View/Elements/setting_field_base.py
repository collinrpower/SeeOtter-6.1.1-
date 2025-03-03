from abc import abstractmethod
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tooltip import MDTooltip

from Config.otter_checker_config import OtterCheckerConfig
from Controller.settings_controller import SettingsController
from View.Elements.setting_field_interface import SettingFieldInterface


class MDTooltipLabel(MDLabel, MDTooltip):

    def __draw_shadow__(self, origin, end, context=None):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tooltip_display_delay = OtterCheckerConfig.instance().TOOLTIP_DELAY


class SettingFieldBase(GridLayout, SettingFieldInterface):

    field_changed = None
    label_width = 300
    label_font_size = 14
    error_label = None

    def __init__(self, title, property_name, controller: SettingsController, tooltip="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.tooltip=tooltip
        self.property_name = property_name
        self.settings_controller = controller
        self.build()
        self.load_config_value()
        self.bind_settings_changed()
        self.settings_controller.register(self)

    def build(self):
        self.height = 22
        self.cols = 3
        self.size_hint = (1, None)
        self.spacing = 10

        label = MDTooltipLabel(text=self.title,
                               size_hint=(None, 1),
                               theme_text_color="Secondary",
                               width=SettingFieldBase.label_width,
                               font_size=SettingFieldBase.label_font_size)
        if self.tooltip:
            label.tooltip_text = self.tooltip

        self.error_label = MDLabel(theme_text_color="Error", font_style="Body2")

        self.add_widget(label)
        self.add_widget(self.get_content())
        self.add_widget(self.error_label)

    def update_config(self):
        self.settings_controller.set_config_value(self.property_name, self.get_value())

    def load_config_value(self):
        self.set_value(self.settings_controller.get_config_value(self.property_name))

    def load_default_config_value(self):
        self.set_value(self.settings_controller.get_default_config_value(self.property_name))

    def on_setting_changed(self, *args, **kwargs):
        self.settings_controller.settings_changed = True

    @abstractmethod
    def validate(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_content(self):
        pass

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def bind_settings_changed(self):
        pass
