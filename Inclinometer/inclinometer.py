from abc import abstractmethod
from typing import List
from Inclinometer.inclinometer_record import InclinometerRecord


class Inclinometer:

    swap_x_y = False
    invert_x = False
    invert_y = False
    invert_z = False

    @abstractmethod
    def load(self, path) -> (List[InclinometerRecord]):
        pass
