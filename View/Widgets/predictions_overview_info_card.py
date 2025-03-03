from kivymd.uix.label import MDLabel

from SurveyEntities.survey import Survey
from View.Elements.property_row import PropertyRow
from View.Elements.stack_card import StackCard
from View.Widgets.pie_chart import PieChart


class PredictionsOverviewInfoCard(StackCard):

    chart = None
    spacer = None

    def __init__(self, title, controller, **kwargs):
        super().__init__(title, **kwargs)
        self.height = 470
        self.controller = controller
        self.controller.bind(survey=self.update_fields)
        self.build()
        self.update_fields()

    def build(self):
        self.predictions = PropertyRow("Predictions")
        self.validated = PropertyRow("Validated")
        self.unvalidated = PropertyRow("Unvalidated")
        self.correct = PropertyRow("Validated Correct")
        self.incorrect = PropertyRow("Validated Incorrect")
        self.ambiguous = PropertyRow("Validated Ambiguous")
        self.spacer = MDLabel(size_hint_y=.5)

        self.add(self.predictions)
        self.add(self.validated)
        self.add(self.unvalidated)
        self.add(self.correct)
        self.add(self.incorrect)
        self.add(self.ambiguous)

        self.add_pie_chart()

    def add_pie_chart(self):
        survey = self.controller.survey
        if not survey:
            return
        if len(self.controller.survey.validated_predictions) > 0:
            validation_fields = {
                "Unvalidated": (len(survey.predictions) - len(survey.validated_predictions), [.4, .4, .4, 1]),
                "Correct": (len(survey.validated_correct_predictions), [.05, .8, .05, 1]),
                "Incorrect": (len(survey.validated_incorrect_predictions), [1, 0, 0, 1]),
                "Ambiguous": (len(survey.validated_ambiguous_predictions), [.3, .6, .9, 1])
            }
        else:
            validation_fields = {
                "N/A": (1, [1, 1, 1, .1])
            }
        position = (200, 100)
        size = (170, 170)
        if self.chart:
            self.remove_widget(self.chart)
            #self.remove_widget(self.spacer)
        self.chart = PieChart(data=validation_fields, position=position, size=size, legend_enable=True)
        self.add_widget(self.chart)
        self.chart.size_hint_y = None
        self.chart.height = 200
        #self.add_widget(self.spacer)

    def clear_fields(self):
        self.predictions.value = ""
        self.validated.value = ""
        self.unvalidated.value = ""
        self.correct.value = ""
        self.incorrect.value = ""
        self.ambiguous.value = ""

    def set_fields(self, survey: Survey):
        self.predictions.value = str(len(survey.predictions))
        self.validated.value = str(len(survey.validated_predictions))
        self.unvalidated.value = str(len(survey.predictions) - len(survey.validated_predictions))
        self.correct.value = str(len(survey.validated_correct_predictions))
        self.incorrect.value = str(len(survey.validated_incorrect_predictions))
        self.ambiguous.value = str(len(survey.validated_ambiguous_predictions))
        self.add_pie_chart()

    def update_fields(self, *args, **kwargs):
        survey = self.controller.survey
        if survey and isinstance(self.controller.survey, Survey):
            self.set_fields(survey)
        else:
            self.clear_fields()
