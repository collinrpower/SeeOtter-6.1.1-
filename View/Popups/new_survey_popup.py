import os
import tkinter as tk
from tkinter import filedialog
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from Controller.see_otter_controller_base import SeeOtterControllerBase
from Controller.survey_command_controller import SurveyCommandController
from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey
from View.Elements.survey_action_button import SurveyActionButton
from View.Elements.toggle_label import ToggleLabel
from View.Elements.transparent_icon_button import TransparentIconButton
from View.Popups.create_survey_from_waldo_data_popup import CreateSurveyFromWaldoDataPopup
from config import PANEL_SPACING, PANEL_PADDING


class NewSurveyPopup(Popup):
    use_default_image_dir = BooleanProperty(defaultvalue=True)

    def __init__(self, command_controller: SurveyCommandController, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(**kwargs)
        self.command_controller = command_controller
        self.controller = controller
        self.title = "New Survey"
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size = (950, 350)
        self.build()
        self.bind_events()
        self.on_use_default_image_dir()

    def build(self):
        layout = RelativeLayout()

        text_box_width = 675

        content_layout = MDBoxLayout(orientation="vertical", pos_hint={"left": 1, "top": 1}, spacing=PANEL_SPACING,
                                     padding=PANEL_PADDING)
        self.project_name_text_field = MDTextField(helper_text_mode="on_focus", hint_text="Project Name",
                                                   size_hint_x=None, width=text_box_width, required=True)
        project_dir_row = MDStackLayout(orientation="lr-tb", size_hint_y=None, height=75, spacing=PANEL_SPACING)
        img_dir_row = MDStackLayout(orientation="lr-tb", size_hint_y=None, height=75, spacing=PANEL_SPACING)
        self.project_dir_text_field = MDTextField(helper_text_mode="on_focus", hint_text="Project Path",
                                                  helper_text="Path to new project", required=True,
                                                  size_hint_x=None, width=text_box_width)
        project_dir_button = TransparentIconButton(callback=self.open_select_project_dir_dialog, icon="folder",
                                                   tooltip="Select Project Path", size_hint_x=None, width=60,
                                                   md_bg_color=(.1, .1, .1, 1))
        self.img_dir_text_field = MDTextField(helper_text_mode="on_focus", hint_text="Images Path",
                                              helper_text="Path to Images (Leaving blank will create empty 'Images' "
                                                          "folder)", required=True,
                                              size_hint_x=None, width=text_box_width)
        self.img_dir_button = TransparentIconButton(callback=self.open_select_image_dir_dialog, icon="folder",
                                                    tooltip="Select Images Path", size_hint_x=None, width=60,
                                                    md_bg_color=(.1, .1, .1, 1))
        self.create_survey_from_waldo_data_popup = CreateSurveyFromWaldoDataPopup(controller=self.controller)
        self.create_from_waldo_data_button = SurveyActionButton(text="Create Survey from Waldo Data",
                                                                controller=self.controller,
                                                                on_press=self.create_survey_from_waldo_data_popup.open)
        img_dir_use_default_checkbox = MDCheckbox(size_hint=(None, None), height=50, width=50,
                                                  pos_hint={"center_x": .5, "center_y": .5})
        img_dir_use_default_checkbox.active = self.use_default_image_dir
        img_dir_use_default_checkbox.bind(active=self.setter('use_default_image_dir'))
        img_dir_use_default_label = MDLabel(text="Use Default Location", theme_text_color="Hint",
                                            size_hint=(None, None), pos_hint={"center_x": .5, "center_y": .5},
                                            height=50, width=100)

        bottom_buttons_row = MDBoxLayout(orientation="horizontal", spacing=PANEL_SPACING * 2, padding=PANEL_PADDING,
                                         pos_hint={"bottom": 1, "right": 1})
        bottom_buttons_row.add_widget(self.create_from_waldo_data_button)
        bottom_buttons_row.add_widget(MDLabel(size_hint_x=.8))
        self.create_button = MDRaisedButton(text="Create", on_press=self.create_button_pressed, disabled=True)
        bottom_buttons_row.add_widget(self.create_button)
        bottom_buttons_row.add_widget(MDRectangleFlatButton(text="Cancel", on_press=self.cancel_button_pressed))

        project_dir_row.add_widget(self.project_dir_text_field)
        project_dir_row.add_widget(project_dir_button)

        img_dir_row.add_widget(self.img_dir_text_field)
        img_dir_row.add_widget(self.img_dir_button)
        img_dir_row.add_widget(img_dir_use_default_checkbox)
        img_dir_row.add_widget(img_dir_use_default_label)

        # content_layout.add_widget(MDLabel(size_hint_y=None, height=10))
        content_layout.add_widget(self.project_name_text_field)
        content_layout.add_widget(project_dir_row)
        content_layout.add_widget(img_dir_row)
        content_layout.add_widget(MDLabel(size_hint_y=.3))

        layout.add_widget(content_layout)
        layout.add_widget(bottom_buttons_row)

        self.content = layout

    def open_select_image_dir_dialog(self, *args):
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title="Select Images Folder")
        if os.path.exists(path):
            self.img_dir_text_field.text = path
        else:
            print(f"Folder does not exist: {path}")

    def open_select_project_dir_dialog(self, *args):
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title="Select Images Folder")
        if os.path.exists(path):
            self.project_dir_text_field.text = path
        else:
            print(f"Folder does not exist: {path}")

    def on_use_default_image_dir(self, *args, **kwargs):
        print(f"Use Default Image Dir: {self.use_default_image_dir}")
        if self.use_default_image_dir:
            self.img_dir_text_field.disabled = True
            self.img_dir_button.disabled = True
        else:
            self.img_dir_text_field.disabled = False
            self.img_dir_button.disabled = False

    def on_project_path_text(self, *args, **kwargs):
        project_dir_text = self.project_dir_text_field.text
        if self.use_default_image_dir:
            if project_dir_text == "":
                self.img_dir_text_field.text = ""
            else:
                self.img_dir_text_field.text = self.project_dir_text_field.text + "/Images"

    def create_button_pressed(self, *args, **kwargs):
        self.command_controller.create_new_survey(survey_name=self.project_name_text_field.text,
                                                  survey_path=self.project_dir_text_field.text,
                                                  images_dir=self.img_dir_text_field.text,
                                                  survey_type=WaldoSurvey)
        self.dismiss()

    def cancel_button_pressed(self, *args, **kwargs):
        print("Create survey cancelled")
        self.dismiss()

    def validate_fields(self, *args):
        if self.project_dir_text_field.text == "" \
                or self.project_name_text_field == "" \
                or self.img_dir_text_field == "":
            self.create_button.disabled = True
        else:
            self.create_button.disabled = False

    def bind_events(self):
        self.project_dir_text_field.bind(text=self.on_project_path_text)
        self.project_name_text_field.bind(text=self.validate_fields)
        self.project_dir_text_field.bind(text=self.validate_fields)
        self.img_dir_text_field.bind(text=self.validate_fields)
