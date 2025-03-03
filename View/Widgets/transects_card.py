import os

from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from View.Elements.property_row import PropertyRow
from View.Widgets.property_stack_card import PropertyStackCard


class TransectsCard(PropertyStackCard):

    def __init__(self, controller: SeeOtterControllerBase, title, **kwargs):
        super().__init__(controller, title, **kwargs)
        self.height = 180

    def build(self):
        self.add_header_button(text="Open Folder", callback=self.controller.open_transects_dir)
        
        self.kml_file_name = PropertyRow("Transect File")
        self.transects_loaded = PropertyRow("File Loaded")
        self.num_transects = PropertyRow("Transects")
        self.on_transect_images = PropertyRow("On-Transect Images")
        self.off_transect_images = PropertyRow("Off-Transect Images")

        self.add(self.kml_file_name)
        self.add(self.transects_loaded)
        self.add(self.num_transects)
        self.add(self.on_transect_images)
        self.add(self.off_transect_images)

    def set_fields(self, survey: Survey):
        if survey.transects and len(survey.transects) > 0:
            self.transects_loaded.value = "True"
            self.num_transects.value = str(len(survey.transects))
            self.on_transect_images.value = str(len(survey.on_transect_images))
            self.off_transect_images.value = str(len(survey.off_transect_images))
        else:
            self.clear_fields()
            self.transects_loaded.value = "False"

        kml_files = [file for file in os.listdir(survey.transect_dir) if file.endswith(".kml")]
        num_kml_files = len(kml_files)
        if num_kml_files == 1:
            self.kml_file_name.value = kml_files[0]
        if num_kml_files == 0:
            self.kml_file_name.value = "No kml transect files found"
        if num_kml_files > 1:
            self.kml_file_name.value = f"Warning: Found multiple kml files in transect folder."
