from abc import abstractmethod

from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

from config import PANEL_SPACING, PANEL_PADDING


class CommandPopup(Popup):

    status_message = StringProperty()
    status_message_label = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Sample Text"
        self.layout = RelativeLayout()
        self.add_widget(self.layout)
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size = (600, 250)
        self.build()
        self.add_buttons()
        self.add_status_message_label()
        self.bind_events()

    def add_buttons(self):
        button_row = MDBoxLayout(orientation="horizontal", pos_hint={"bottom": 1, "right": 1}, size_hint=(None, None),
                                 size=(200, 100), spacing=PANEL_SPACING, padding=PANEL_PADDING)
        button_row.add_widget(MDRaisedButton(text="Run", on_press=self.run_command))
        button_row.add_widget(MDRaisedButton(text="Cancel", on_press=self.dismiss))
        self.layout.add_widget(button_row)

    def add_status_message_label(self):
        self.status_message_label = MDLabel(pos_hint={"bottom": 1, "left": 1}, size_hint=(None, None),
                                            padding=(10, 10),
                                            theme_text_color="Secondary", size=(self.width-200, 50))
        self.layout.add_widget(self.status_message_label)

    def on_status_message(self, *args, **kwargs):
        self.status_message_label.text = self.status_message

    def set_status(self, message, is_error=False):
        self.status_message_label.theme_text_color = "Error" if is_error else "Secondary"
        self.status_message_label.text = message

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def run_command(self, *args, **kwargs):
        pass

    def bind_events(self):
        pass
