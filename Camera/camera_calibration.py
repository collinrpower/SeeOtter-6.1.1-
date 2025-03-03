from Utilities.json_convert import JsonConvert


@JsonConvert.register
class CameraCalibration(object):
    """
    Contains information about camera rotation/orientation. Can also be used as a
    calibration to represent the angle offset needed to optimize accuracy.
    """
    def __init__(self, angle_x=0, angle_y=0, angle_z=0, gps_delay_offset=0, altitude_offset=0, hfov=0):

        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angle_z
        self.hfov = hfov
        self.gps_delay_offset = gps_delay_offset
        self.altitude_offset = altitude_offset

    def __add__(self, other):
        sum_calibration = CameraCalibration()
        for attr in ["angle_x", "angle_y", "angle_z", "hfov", "gps_delay_offset",  "altitude_offset"]:
            self_val = getattr(self, attr)
            other_val = getattr(other, attr)
            setattr(sum_calibration, attr, self_val + other_val)
        return sum_calibration

    def get_rotation(self):
        return [self.angle_x, self.angle_y, self.angle_z]

    def __str__(self):
        return f"Rotation: [{self.angle_x}, {self.angle_y}, {self.angle_z}], " \
               f"altitude offset: {self.altitude_offset}, hfov: {self.hfov} "
