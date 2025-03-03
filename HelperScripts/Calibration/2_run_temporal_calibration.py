from Calibration.calibration_settings import CalibrationSettings
from Calibration.temporal_calibration import TemporalCalibration
from Calibration.temporal_point import TemporalPoint
from Utilities.utilities import print_title, prompt_user
from config import NEWLINE
from select_survey import load_survey

###########################################################
calibration_settings = CalibrationSettings.small()
###########################################################

survey = load_survey()
temporal_calibration = TemporalCalibration(survey=survey)
temporal_calibration.run_calibration(calibration_settings=calibration_settings)


print_title(f"Calibration Complete\n\n{NEWLINE.join([str(camera) for camera in survey.camera_system.cameras])}")
response = prompt_user("Save calibrated camera settings? [Y/N]")
if response is True:
    survey.save()
