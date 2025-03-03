from enum import Enum
from Utilities.json_convert import JsonConvert
from Camera.camera_calibration import CameraCalibration


class CALIBRATION_INCREMENT_SIZE(Enum):
    VERY_FINE = 0
    FINE = 1
    MEDIUM = 2
    WIDE = 3
    VERY_WIDE = 4


@JsonConvert.register
class CalibrationSettings:
    """
    Defines the range of values and increment size for running a camera calibration

    center_point: Center values for calibration
    range: How far from center point calibration will run (center_point +- range)
    min_calibration: Starting values for each CameraCalibration setting
    max_calibration: Max values for each CameraCalibration setting
    calibration_increment: Amount each setting is incremented during calibration
    """

    def __init__(self, range: CameraCalibration = None,
                 increment: CameraCalibration = None,
                 center_point: CameraCalibration = CameraCalibration(),
                 calibrate_cameras_independently=False,
                 calibrate_inclinometer=False):

        # False -> Same calibration will be applied to every camera system (relative camera orientation retained)
        # True  -> Each camera will be calibrated independently (relative camera orientation altered, requires )
        self.calibrate_cameras_independently = calibrate_cameras_independently
        # Is this calibration being used to calibrate images with inclinometer data
        self.calibrate_inclinometer = calibrate_inclinometer
        self.center_point = center_point
        self.range = range
        self.increment = increment
        self.validate_settings()

    def get(self):
        return self.min_calibration, self.max_calibration, self.increment

    def validate_settings(self):
        if self.range is None or self.increment is None:
            return
        attributes = ["angle_x", "angle_y", "angle_z", "hfov"]
        for attr_name in attributes:
            rng = getattr(self.range, attr_name)
            inc = getattr(self.increment, attr_name)
            if inc < 0 or rng < 0:
                raise ValueError(f"Values for range and increment cannot be negative. "
                                 f"Attr: {attr_name}, Range: {rng}, Increment: {inc}")
            if rng > 0 and inc == 0:
                raise ValueError(f"Increment must be > 0 if range is specified. "
                                 f"Attr: {attr_name}, Range: {rng}, Increment: {inc}")
            if rng == 0 and inc == 0:
                # Set increment to 1 if no range specified so we don't get stuck in an infinite loop
                setattr(self.increment, attr_name, 1)

    @property
    def min_calibration(self):
        return CameraCalibration(
            angle_x=self.center_point.angle_x - self.range.angle_x / 2,
            angle_y=self.center_point.angle_y - self.range.angle_y / 2,
            angle_z=self.center_point.angle_z - self.range.angle_z / 2,
            hfov=self.center_point.hfov - self.range.hfov / 2,
            gps_delay_offset=self.center_point.gps_delay_offset - self.range.gps_delay_offset / 2,
        )

    @property
    def max_calibration(self):
        return CameraCalibration(
            angle_x=self.center_point.angle_x + self.range.angle_x / 2,
            angle_y=self.center_point.angle_y + self.range.angle_y / 2,
            angle_z=self.center_point.angle_z + self.range.angle_z / 2,
            hfov=self.center_point.hfov + self.range.hfov / 2,
            gps_delay_offset=self.center_point.gps_delay_offset + self.range.gps_delay_offset / 2,
        )

    @staticmethod
    def small():
        return CalibrationSettings(
            range=CameraCalibration(angle_x=20, angle_y=20, angle_z=8),
            increment=CameraCalibration(angle_x=2, angle_y=2, angle_z=1)
        )

    @staticmethod
    def medium():
        return CalibrationSettings(
            range=CameraCalibration(angle_x=30, angle_y=30, angle_z=12),
            increment=CameraCalibration(angle_x=1, angle_y=1, angle_z=1)
        )

    @staticmethod
    def large():
        return CalibrationSettings(
            range=CameraCalibration(angle_x=30, angle_y=30, angle_z=12),
            increment=CameraCalibration(angle_x=.5, angle_y=.5, angle_z=.5)
        )
