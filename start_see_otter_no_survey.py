import os
import sys
from kivy.resources import resource_add_path
from View.Windows.see_otter_window import SeeOtterWindow

"""
Start OtterChecker using the survey currently selected by 'select_survey.py'
"""

# For PyInstaller
if hasattr(sys, '_MEIPASS'):
    resource_add_path(os.path.join(sys._MEIPASS))

SeeOtterWindow().run()
print("Exiting...")
