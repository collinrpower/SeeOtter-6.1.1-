from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from Controller.see_otter_controller import SeeOtterController

Builder.load_string('''
<Content>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: "waldo_data_path_text_field"
        hint_text: "Path to Waldo Data"

''')


class Content(BoxLayout):
    pass


class CreateSurveyFromWaldoDataDialog(Widget):
    dialog = None
    waldo_data_path_text_field = None

    def __init__(self, controller: SeeOtterController, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        # self.size_hint_y = None
        # self.type = "custom"
        # self.height = 300
        # self.spacing = 10

    def open(self, *args, **kwargs):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Address:",
                type="custom",
                content_cls=Content(),
                size_hint=(None, None),
                size=(500, 300),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        # text_color=self.theme_cls.primary_color,
                        on_release=lambda _: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        # text_color=self.theme_cls.primary_color,
                        on_release=self.run_command
                    ),
                ],
            )
        self.dialog.open()

    # def build(self):
    #     self.dialog = MDDialog()
    #     layout = BoxLayout(orientation="vertical", size_hint_y=None, height=300)
    #     self.waldo_data_path_text_field = MDTextField(hint_text="Path to Waldo Data")
    #     layout.add_widget(self.waldo_data_path_text_field)
    #
    #     self.buttons = [
    #                 MDFlatButton(
    #                     text="Cancel",
    #                     theme_text_color="Custom",
    #                     text_color=self.theme_cls.primary_color,
    #                     on_press=self.dismiss
    #                 ),
    #                 MDFlatButton(
    #                     text="Run",
    #                     theme_text_color="Custom",
    #                     text_color=self.theme_cls.primary_color,
    #                     on_press=self.run_command
    #                 )
    #             ]

    def run_command(self, *args, **kwargs):
        waldo_data_path_text_field = self.dialog.ids["waldo_data_path_text_field"]
        print(f"Running command: {waldo_data_path_text_field.text}")
