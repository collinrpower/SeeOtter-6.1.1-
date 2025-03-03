from abc import abstractmethod
from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from Utilities.utilities import class_name
from View.Elements.property_row import PropertyRow
from View.Elements.stack_card import StackCard


class PropertyStackCard(StackCard):

    def __init__(self, controller: SeeOtterControllerBase, title, **kwargs):
        super().__init__(title, **kwargs)
        self.controller = controller
        self.property_rows = []
        self.build()
        self.controller.bind(survey=self.update_fields)
        self.update_fields()

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def set_fields(self, survey: Survey):
        pass

    def add(self, widget):
        if isinstance(widget, PropertyRow):
            self.property_rows.append(widget)
        super().add(widget)

    def clear_fields(self):
        for property_row in self.property_rows:
            property_row.value = ""

    def update_fields(self, *args, **kwargs):
        survey = self.controller.survey
        try:
            if survey and isinstance(self.controller.survey, Survey):
                self.set_fields(survey)
            else:
                self.clear_fields()
        except Exception as ex:
            self.controller.set_snackbar_message(f"Error occurred while trying to update card "
                                                 f"({class_name(self)}): {ex}")
