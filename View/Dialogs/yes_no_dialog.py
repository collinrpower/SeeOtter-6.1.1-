from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog


class YesNoDialog(MDDialog):

    def __init__(self, message, yes_action, no_action=None, **kwargs):
        self.yes_action = yes_action
        self.no_action = no_action
        self.auto_dismiss = False
        super().__init__(title="Notification",
                         text=message,
                         buttons=[
                             MDRaisedButton(
                                 text="Yes",  # text_color=self.theme_cls.primary_color,
                                 on_release=self.yes_pressed),
                             MDRectangleFlatButton(
                                 text="No",  # text_color=self.theme_cls.primary_color,
                                 on_release=self.no_pressed),
                         ],
                         **kwargs)

    def no_pressed(self, *args, **kwargs):
        self.dismiss()
        if self.no_action:
            self.no_action()

    def yes_pressed(self, *args, **kwargs):
        self.dismiss()
        self.yes_action()
