import os
import tkinter as tk
from tkinter import filedialog
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from Controller.see_otter_controller import SeeOtterController
from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.transparent_icon_button import TransparentIconButton
from View.Popups.command_popup import CommandPopup
from config import PANEL_SPACING, PANEL_PADDING


class CreateSurveyFromWaldoDataPopup(CommandPopup):

    def __init__(self, controller: SeeOtterController, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.title = "Create Survey from Waldo Data"
        self.size = (800, 200)

    def build(self):
        img_dir_row = MDBoxLayout(orientation="horizontal", pos_hint={"top": 1, "left": 1}, size_hint_y=None,
                                  height=75, spacing=PANEL_SPACING, padding=PANEL_PADDING)
        self.waldo_dir_text_field = MDTextField(helper_text_mode="on_focus", hint_text="Path to Waldo Data",
                                                helper_text="Select folder containing a single day of Waldo data",
                                                size_hint_x=None, width=675)
        self.file_selection_button = TransparentIconButton(callback=self.open_select_dir_dialog, icon="folder",
                                                           tooltip="Select Path", size_hint_x=None, width=60,
                                                           md_bg_color=(.1, .1, .1, 1))
        img_dir_row.add_widget(self.waldo_dir_text_field)
        img_dir_row.add_widget(self.file_selection_button)

        self.layout.add_widget(img_dir_row)

    def run_command(self, *args, **kwargs):
        self.controller.commands.create_survey_from_waldo_data(path=self.waldo_dir_text_field.text)
        self.dismiss()

    def open_select_dir_dialog(self, *args, **kwargs):
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title="Select Images Folder")
        if os.path.exists(path):
            self.waldo_dir_text_field.text = path
        else:
            print(f"Folder does not exist: {path}")

    def bind_events(self):
        pass
