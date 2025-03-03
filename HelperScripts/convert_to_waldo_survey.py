from Camera.waldo_camera_system import WaldoCameraSystem
from Inclinometer.hwt905_inclinometer import Hwt905Inclinometer
from SurveyEntities.waldo_survey import WaldoSurvey
from select_survey import load_survey

survey = load_survey()

survey.__class__ = WaldoSurvey
survey.camera_system = WaldoCameraSystem()
survey.inclinometer = Hwt905Inclinometer()
survey.save()
