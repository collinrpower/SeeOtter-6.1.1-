from pathlib import Path
from typing import List
from Camera.camera_system import CameraSystem
from Camera.waldo_camera_system import WaldoCameraSystem
from Inclinometer.hwt905_inclinometer import Hwt905Inclinometer
from SurveyEntities.survey import Survey
from SurveyEntities.survey_image import SurveyImage
from Utilities.WaldoUtilities.waldo_survey_converter import WaldoSurveyConverter
from Utilities.WaldoUtilities.waldo_survey_path import WaldoSurveyPath


class WaldoSurvey(Survey):

    def __init__(self, survey_name, survey_path=None, images_dir=None, camera_system=None,
                 images: List[SurveyImage] = None, inclinometer=None):
        super().__init__(survey_name, survey_path=survey_path, images_dir=images_dir,
                         camera_system=camera_system or WaldoCameraSystem(),
                         images=images, inclinometer=inclinometer or Hwt905Inclinometer())

    @staticmethod
    def create_from_waldo_survey(path, local_project: bool = False):
        image_dir = WaldoSurveyConverter.run_for_day(path)
        survey_name = WaldoSurveyConverter.get_project_name_from_survey_path(path)
        survey_path = None if local_project else Path(image_dir).parent.absolute()
        return WaldoSurvey.new(survey_name=survey_name, images_dir=image_dir, survey_path=survey_path, overwrite=True,
                               force=True)
