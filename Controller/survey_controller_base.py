from functools import partial
from pathlib import Path

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty
from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey
from Utilities.custom_exceptions import SurveyVersionException


class SurveyControllerBase(EventDispatcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    program_status_message = StringProperty("")
    survey = ObjectProperty(allownone=True)

    def set_survey(self, survey: Survey, gui_threadsafe=False):
        if gui_threadsafe:
            Clock.schedule_once(partial(self.set_survey, survey), -1)
        else:
            self.survey = survey

    # def load_survey(self, survey, update_status_message=True, *args):
    #     if update_status_message:
    #         self.program_status_message = f"Loading survey: {survey}"
    #         Clock.schedule_once(partial(self.load_survey, survey, False))
    #         return
    #     if isinstance(survey, Survey):
    #         self.survey = survey
    #     else:
    #         try:
    #             self.survey = Survey.load(survey)
    #         except SurveyVersionException as sve:
    #             survey_path = Path(survey).parent
    #             Survey.upgrade_project_version(survey_path=survey_path, survey_type=WaldoSurvey, force=True)
    #             self.survey = Survey.load(survey)
    #     self.program_status_message = ""
