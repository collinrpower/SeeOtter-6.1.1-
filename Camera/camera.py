import re
from os.path import basename
from Camera.camera_calibration import CameraCalibration
from Inclinometer.inclinometer_record import InclinometerRecord
from Utilities.json_convert import JsonConvert


@JsonConvert.register
class Camera:

    def __init__(self, name="", orientation=CameraCalibration(), default_calibration: CameraCalibration = None,
                 inclinometer_calibration: CameraCalibration = None, image_regex=None, rotate_image=False):

        self.name = name
        self.image_regex = image_regex
        self.rotate_image = rotate_image

        # Orientation of camera system. Default pointing straight down (x, y, z => 0, 0, 0)
        self.orientation = orientation
        # Calibration for images with no tiltometer data
        self.default_calibration = default_calibration
        # Calibration for images with tiltometer data
        self.inclinometer_calibration = inclinometer_calibration

    def __str__(self):
        return f"Camera: {self.name}\n" \
               f"   - Orientation:              {self.orientation}\n" \
               f"   - Default Calibration:      {self.default_calibration}\n" \
               f"   - Inclinometer Calibration: {self.inclinometer_calibration}"

    def get_calibrated_orientation(self, inclinometer_data: InclinometerRecord = None):
        orientation = self.orientation
        if inclinometer_data and self.inclinometer_calibration:
            orientation += self.inclinometer_calibration
            orientation.angle_x += inclinometer_data.angle_x
            orientation.angle_y += inclinometer_data.angle_y
        elif self.default_calibration:
            orientation += self.default_calibration
        return orientation

    def get_calibrated_rotation(self, inclinometer_data=None):
        return self.get_calibrated_orientation(inclinometer_data).get_rotation()

    def is_image_from_this_camera(self, path):
        if self.image_regex == "":
            return True
        if re.search(self.image_regex, basename(path)):
            return True
        return False
