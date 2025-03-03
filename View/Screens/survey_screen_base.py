import os
from tkinter import filedialog
from kivy.uix.screenmanager import Screen
from Controller.survey_controller_base import SurveyControllerBase
import tkinter as tk
from config import SURVEY_SAVE_FILE


class SurveyScreenBase(Screen):

    controller: SurveyControllerBase = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_select_survey_dialog(self, *args):
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Select Survey", filetypes=(("SeeOtter Survey", SURVEY_SAVE_FILE),))
        if os.path.exists(path):
            self.controller.load_survey(path)
        else:
            print(f"Path does not exist: {path}")
