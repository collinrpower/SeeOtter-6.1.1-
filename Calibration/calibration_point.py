from abc import abstractmethod


class CalibrationPoint:

    @abstractmethod
    def get_error(self, ignore_inclinometer=True):
        pass
