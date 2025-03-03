
class InclinometerRecord:

    def __init__(self, datetime=None, angle_x=None, angle_y=None, angle_z=None, acceleration_x=None,
                 acceleration_y=None, acceleration_z=None, angular_velocity_x=None, angular_velocity_y=None,
                 angular_velocity_z=None, hx=None, hy=None, hz=None, temp=None):

        self.datetime = datetime

        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angle_z

        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.acceleration_z = acceleration_z

        self.angular_velocity_x = angular_velocity_x
        self.angular_velocity_y = angular_velocity_y
        self.angular_velocity_z = angular_velocity_z

        self.hx = hx
        self.hy = hy
        self.hz = hz

        self.temp = temp
