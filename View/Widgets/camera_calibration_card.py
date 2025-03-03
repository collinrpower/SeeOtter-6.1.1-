from kivymd.uix.label import MDLabel

from Camera.camera_calibration import CameraCalibration
from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from Utilities.utilities import class_name
from View.Elements.property_row import PropertyRow
from View.Widgets.property_stack_card import PropertyStackCard


class CameraCalibrationCard(PropertyStackCard):

    def __init__(self, calibration: CameraCalibration, controller: SeeOtterControllerBase, title, **kwargs):
        self.calibration = calibration
        super().__init__(controller, title, padding=20,  **kwargs)
        self.height = 160
        #self.md_bg_color = (0, 0, 1, 1)

    def build(self):
        self.angle_x = PropertyRow("Angle(X)")
        self.angle_y = PropertyRow("Angle(Y)")
        self.angle_z = PropertyRow("Angle(Z)")
        self.hfov = PropertyRow("Horizontal FOV")

        self.add(self.angle_x)
        self.add(self.angle_y)
        self.add(self.angle_z)
        self.add(self.hfov)

    def set_fields(self, survey: Survey):
        self.angle_x.value = str(self.calibration.angle_x)
        self.angle_y.value = str(self.calibration.angle_y)
        self.angle_z.value = str(self.calibration.angle_z)
        self.hfov.value = str(self.calibration.hfov)
