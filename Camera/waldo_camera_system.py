from Camera.camera import Camera
from Camera.camera_calibration import CameraCalibration
from Camera.camera_system import CameraSystem
from Utilities.json_convert import JsonConvert
from config import *


@JsonConvert.register
class WaldoCameraSystem(CameraSystem):

    def __init__(self, name="Waldo Camera System", cameras=None):
        left_camera = Camera("Waldo Left Camera", image_regex=WALDO_LEFT_CAMERA_REGEX,
                             orientation=CameraCalibration(angle_y=WALDO_HORIZONTAL_FOV/2, hfov=WALDO_HORIZONTAL_FOV))
        right_camera = Camera("Waldo Right Camera", image_regex=WALDO_RIGHT_CAMERA_REGEX, rotate_image=True,
                              orientation=CameraCalibration(angle_y=-WALDO_HORIZONTAL_FOV/2, hfov=WALDO_HORIZONTAL_FOV))
        super().__init__(name="Waldo Camera System", cameras=[left_camera, right_camera])
