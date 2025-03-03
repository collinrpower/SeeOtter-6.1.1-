from Calibration.temporal_calibration import TemporalCalibration
from Calibration.temporal_point import TemporalPoint
from Utilities.utilities import print_title
from select_survey import load_survey


def print_points(points):
    print_title("Calibration Points:")
    for point in points:
        print(point)


survey = load_survey()
temporal_calibration = TemporalCalibration(survey=survey)

###########################################################
# ADD CALIBRATION POINTS HERE
###########################################################
temporal_calibration.add_calibration_points(
    TemporalPoint('0_000_00_000.jpg', (2429, 667), '0_000_00_001.jpg', (3303, 5451)),
    TemporalPoint('0_000_00_000.jpg', (4667, 1119), '0_000_00_001.jpg', (5496, 5596)),
    TemporalPoint('1_000_00_001.jpg', (3589, 1137), '1_000_00_002.jpg', (4314, 5633)),
    TemporalPoint('1_000_00_001.jpg', (3759, 199), '1_000_00_002.jpg', (4490, 4651)),
    TemporalPoint('1_000_00_001.jpg', (4587, 481), '1_000_00_002.jpg', (5346, 5023))
)
###########################################################

print_points(temporal_calibration.temporal_points)
temporal_calibration.save_calibration_points()
