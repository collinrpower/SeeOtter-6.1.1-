from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from Controller.see_otter_controller_base import SeeOtterControllerBase


class PromptValidatorNamePopup(Popup):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = 'Enter Name'
        self.size_hint = (None, None)
        self.size = (300, 180)
        self.font_size = "18sp"
        self.content = self.build()

    def build(self):
        layout = GridLayout(cols=1, padding=10, spacing=20)
        self.text_input = TextInput(multiline=False)
        submit_button = Button(text="Submit", size_hint_y=None, height=30, on_press=self.on_submit_button_pressed)
        layout.add_widget(self.text_input)
        layout.add_widget(submit_button)
        return layout

    def on_submit_button_pressed(self, *args):
        text = self.text_input.text
        if text is None:
            return
        self.controller.config.VALIDATOR_NAME = text
        self.controller.config.save()
        self.dismiss()
