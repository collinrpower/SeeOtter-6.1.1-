from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup


class ConfirmCloseWithoutSavingPopup(Popup):

    def __init__(self, save_action, continue_without_saving_action, **kwargs):
        super().__init__(**kwargs)
        self.title = "Exit without saving?"
        self.size_hint = (None, None)
        self.size = (300, 200)
        self.font_size = "18sp"
        self.save_action = save_action
        self.continue_without_saving_action = continue_without_saving_action
        self.content = self.build()

    def build(self):
        layout = GridLayout(rows=3, padding=10, spacing=15)
        save_and_exit_button = Button(text="Save and Exit", on_press=self.save_action)
        continue_without_saving_button = Button(text="Exit", on_press=self.continue_without_saving_action)
        cancel_button = Button(text="Cancel", on_press=self.dismiss)
        layout.add_widget(save_and_exit_button)
        layout.add_widget(continue_without_saving_button)
        layout.add_widget(cancel_button)
        return layout
