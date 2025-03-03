import os

from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from Utilities.utilities import class_name
from View.Elements.property_row import PropertyRow
from View.Widgets.property_stack_card import PropertyStackCard


class InclinometerCard(PropertyStackCard):

    def __init__(self, controller: SeeOtterControllerBase, title, **kwargs):
        super().__init__(controller, title, **kwargs)
        self.height = 160

    def build(self):
        self.add_header_button(text="Open Folder", callback=self.controller.open_inclinometer_dir)

        self.inclinometer_type = PropertyRow("Inclinometer", label_size_hint_x=.6)
        self.inclinometer_files = PropertyRow("Inclinometer files", label_size_hint_x=.6)
        self.images_with_inclinometer_data = PropertyRow("Images with inclinometer data", label_size_hint_x=.6)
        self.images_without_inclinometer_data = PropertyRow("Images without inclinometer data", label_size_hint_x=.6)

        self.add(self.inclinometer_type)
        self.add(self.inclinometer_files)
        self.add(self.images_with_inclinometer_data)
        self.add(self.images_without_inclinometer_data)

    def set_fields(self, survey: Survey):
        inclinometer = survey.inclinometer
        if inclinometer:
            self.inclinometer_type.value = class_name(inclinometer)
            self.inclinometer_files.value = str(len([file for file in os.listdir(survey.inclinometer_dir)]))
            self.images_with_inclinometer_data.value = str(len(survey.images_with_inclinometer_data))
            self.images_without_inclinometer_data.value = str(len(survey.images_without_inclinometer_data))
        else:
            self.inclinometer_type.value = "None"
