from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from Controller.see_otter_controller_base import SeeOtterControllerBase


class ProgramStatusPopup(Popup):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.controller.bind(program_status_message=self.on_program_status_message)
        self.auto_dismiss = False
        self.title = ""
        self.separator_height = 0
        self.size_hint = (None, None)
        self.size = (600, 100)
        self.font_size = "18sp"
        self.label = Label(text="Sample Text", size_hint=(None, None))
        layout = AnchorLayout(anchor_x="center", anchor_y="center")
        layout.add_widget(self.label)
        self.content = layout

    def on_program_status_message(self, *args):
        message = self.controller.program_status_message
        print("Status message: " + message)
        self.label.text = message
        if message == "":
            self.dismiss()
        else:
            self.open()
