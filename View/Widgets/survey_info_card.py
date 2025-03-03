from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from Utilities.utilities import format_percent_str
from View.Elements.property_row import PropertyRow
from View.Widgets.property_stack_card import PropertyStackCard


class SurveyInfoCard(PropertyStackCard):

    def __init__(self, controller: SeeOtterControllerBase, title, **kwargs):
        super().__init__(controller, title, **kwargs)
        self.height = 280

    def build(self):
        self.add_header_button(text="Open Folder", callback=self.controller.open_survey_dir)

        self.survey_name = PropertyRow("Survey")
        self.version = PropertyRow("Version")
        self.survey_type = PropertyRow("Survey Type")
        self.project_path = PropertyRow("Project Path")
        self.image_dir = PropertyRow("Image Directory")
        self.images = PropertyRow("Images")
        self.pre_processed_images = PropertyRow("Pre-Processed")
        self.processed_images = PropertyRow("Processed")
        self.excluded = PropertyRow("Excluded")

        self.add(self.survey_name)
        self.add(self.version)
        self.add(self.survey_type)
        self.add(self.project_path)
        self.add(self.image_dir)
        self.add(self.images)
        self.add(self.pre_processed_images)
        self.add(self.processed_images)
        self.add(self.excluded)

    def set_fields(self, survey: Survey):

        num_images = survey.num_images
        num_pre_processed = len(survey.pre_processed_images)
        num_processed = len(survey.processed_images)
        pre_processed_percent = f"({format_percent_str(current=num_pre_processed, max=num_images, no_decimals=True)})" \
            if survey.has_images else ""
        processed_percent = f"({format_percent_str(current=num_processed, max=num_images, no_decimals=True)})" \
            if survey.has_images else ""

        self.survey_name.value = survey.survey_name
        self.version.value = str(survey.version)
        self.survey_type.value = str(type(survey).__name__)
        self.project_path.value = str(survey.project_path)
        self.image_dir.value = str(survey.images_dir)
        self.images.value = str(num_images)
        self.pre_processed_images.value = f"{num_pre_processed}   {pre_processed_percent}"
        self.processed_images.value = f"{num_processed}   {processed_percent}"
        self.excluded.value = str(len(survey.excluded_images))
