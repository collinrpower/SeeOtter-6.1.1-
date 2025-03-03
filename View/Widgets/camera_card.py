from kivymd.uix.label import MDLabel
from kivymd.uix.stacklayout import MDStackLayout

from Camera.camera import Camera
from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from Utilities.utilities import class_name
from View.Elements.bool_property_field import BoolPropertyField
from View.Elements.property_row import PropertyRow
from View.Elements.string_property_field import StringPropertyField
from View.Widgets.camera_calibration_card import CameraCalibrationCard
from View.Widgets.property_stack_card import PropertyStackCard


class CameraCard(PropertyStackCard):

    def __init__(self, title, controller, camera: Camera, **kwargs):
        self.camera = camera
        super().__init__(title=title, controller=controller, padding=20, **kwargs)
        self.height = 300
        self.md_bg_color = (0, 0, 0, .3)

    def build(self):
        self.camera_name = PropertyRow("Camera Name")
        self.rotate_image = PropertyRow("Rotate Image on Pre-Processing")
        self.image_regex = PropertyRow("Image Identifier Regex")

        self.camera_orientation = CameraCalibrationCard(title="Camera Orientation",
                                                 calibration=self.camera.orientation,
                                                 controller=self.controller)
        if self.camera.default_calibration:
            self.default_calibration = CameraCalibrationCard(title="Default Calibration", controller=self.controller,
                                                             calibration=self.camera.default_calibration)
        else:
            self.default_calibration = PropertyRow("Default Calibration")
        if self.camera.inclinometer_calibration:
            self.inclinometer_calibration = CameraCalibrationCard(title="Inclinometer Calibration",
                                                                  calibration=self.camera.inclinometer_calibration,
                                                                  controller=self.controller)
        else:
            self.inclinometer_calibration = PropertyRow("Inclinometer Calibration")

        self.add(self.rotate_image)
        self.add(self.camera_orientation)
        self.add(self.default_calibration)
        self.add(self.inclinometer_calibration)
        self.add(MDLabel(size_hint_y=.5))

    def set_fields(self, survey: Survey):
        self.rotate_image.value = str(self.camera.rotate_image)
        if isinstance(self.default_calibration, PropertyRow):
            self.default_calibration.value = "None"
        if isinstance(self.inclinometer_calibration, PropertyRow):
            self.inclinometer_calibration.value = "None"