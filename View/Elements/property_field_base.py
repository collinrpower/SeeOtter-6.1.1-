from abc import abstractmethod

from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel


class PropertyFieldBase(GridLayout):

    label_width = 300
    label_font_size = 14

    error_label = None
    error_text = StringProperty()

    def __init__(self, title, obj, property_name, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.obj = obj
        self.property_name = property_name

    def build(self):
        self.height = 22
        self.cols = 3
        self.size_hint = (1, None)
        self.spacing = 10

        label = MDLabel(text=self.title,
                        size_hint=(None, 1),
                        theme_text_color="Secondary",
                        width=PropertyFieldBase.label_width,
                        font_size=PropertyFieldBase.label_font_size)

        self.error_label = MDLabel(theme_text_color="Error", font_style="Body2")

        self.add_widget(label)
        self.add_widget(self.get_content())
        self.add_widget(self.error_label)

    def update_property(self):
        setattr(self.obj, self.property_name, self.get_value())

    def update_field(self):
        prop_value = getattr(self.obj, self.property_name)
        self.set_value(value=prop_value)

    @abstractmethod
    def get_content(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def get_value(self):
        pass
