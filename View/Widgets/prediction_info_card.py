from Controller.see_otter_controller_base import SeeOtterControllerBase
from Processing.survey_image_processing import get_prediction_dimensions
from SurveyEntities.object_prediction_data import ObjectPredictionData
from Utilities.custom_exceptions import NoCameraSystemException
from View.Elements.property_row import PropertyRow
from View.Elements.stack_card import StackCard


class PredictionInfoCard(StackCard):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__("Selected Prediction Info", **kwargs)
        self.controller = controller
        self.size_hint_y = None
        self.height = 150
        self.controller.bind(current_prediction=self.update_fields)
        self.build()

    def build(self):
        self.category_name = PropertyRow("Category Name")
        self.latitude = PropertyRow("Latitude")
        self.longitude = PropertyRow("Longitude")
        self.box_size = PropertyRow("Box Size (m)")

        self.add(self.category_name)
        self.add(self.latitude)
        self.add(self.longitude)
        self.add(self.box_size)

    def update_fields(self, value, instance):
        prediction: ObjectPredictionData = self.controller.current_prediction
        if prediction:
            self.category_name.value = prediction.category_name
            self.latitude.value = str(prediction.latitude)
            self.longitude.value = str(prediction.longitude)
            try:
                dimensions = get_prediction_dimensions(self.controller.current_image, prediction)
                self.box_size.value = f"{dimensions[0]:0.1f} x {dimensions[1]:0.1f}"
            except NoCameraSystemException as ncse:
                self.box_size.value = f"N/A (No Camera System)"
            except Exception:
                self.box_size.value = "N/A"
        else:
            self.category_name.value = ""
            self.latitude.value = ""
            self.longitude.value = ""
            self.box_size.value = ""
