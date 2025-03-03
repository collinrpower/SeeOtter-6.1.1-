from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from Controller.see_otter_controller import SeeOtterController


class SurveyActionButton(MDRaisedButton):

    def __init__(self, controller: SeeOtterController, show_confirmation=False, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.size_hint_x = None
        self.width = 500
