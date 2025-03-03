from Controller.see_otter_controller import SeeOtterController
from Controller.see_otter_controller_base import SeeOtterState
from SurveyEntities.survey import Survey
from View.Elements.card_section_header import CardSectionHeader
from View.Elements.stack_card import StackCard
from View.Elements.survey_action_button import SurveyActionButton


class SurveyActionsCard(StackCard):

    def __init__(self, controller: SeeOtterController, title, **kwargs):
        super().__init__(title, **kwargs)
        self.controller = controller
        self.height = 560
        self.build()
        self.controller.bind(state=self.on_state_changed)
        self.on_state_changed()

    def build(self):
        commands = self.controller.commands
        self.add(CardSectionHeader(text="Processing"))
        self.add(SurveyActionButton(text="Run Pre-Processing", controller=self.controller,
                                    on_press=commands.run_pre_processing))
        self.add(SurveyActionButton(text="Force Run Pre-Processing", controller=self.controller,
                                    on_press=commands.force_run_pre_processing))
        self.add(SurveyActionButton(text="Run Post-Processing", controller=self.controller,
                                    on_press=commands.run_post_processing))

        self.add(CardSectionHeader(text="Survey Management"))
        self.add(SurveyActionButton(text="Create Backup", controller=self.controller,
                                    on_press=commands.create_backup))
        self.add(SurveyActionButton(text="Reset All Validations", controller=self.controller,
                                    on_press=commands.reset_all_validations))
        self.add(SurveyActionButton(text="Reset All Predictions", controller=self.controller,
                                    on_press=commands.reset_all_predictions))

        self.add(CardSectionHeader(text="Files and Data"))
        self.add(SurveyActionButton(text="Reload Inclinometer Data", controller=self.controller,
                                    on_press=commands.reload_inclinometer_data))
        self.add(SurveyActionButton(text="Reload Image Metadata", controller=self.controller,
                                    on_press=commands.reload_image_metadata))
        self.add(SurveyActionButton(text="Reload Transects", controller=self.controller,
                                    on_press=commands.reload_transects))

        self.add(CardSectionHeader(text="Data Generation"))
        self.add(SurveyActionButton(text="Generate Annotations", controller=self.controller,
                                    on_press=commands.generate_annotations))
        self.add(SurveyActionButton(text="Clone Filtered Survey", controller=self.controller,
                                    on_press=self.controller.open_clone_filtered_survey_popup))
        self.add(CardSectionHeader(text="Other"))
        self.add(SurveyActionButton(text="Vote Ambiguous Validations", controller=self.controller,
                                    on_press=commands.vote_ambiguous_validations))

    def some_action(self, *args, **kwargs):
        print("Some action happened.")

    def clear_fields(self):
        pass

    def set_fields(self, survey: Survey):
        pass

    def update_fields(self, *args, **kwargs):
        survey = self.controller.survey
        if survey and isinstance(self.controller.survey, Survey):
            self.set_fields(survey)
        else:
            self.clear_fields()

    def on_state_changed(self, *args, **kwargs):
        if self.controller.state == SeeOtterState.SURVEY_LOADED:
            self.disabled = False
        else:
            self.disabled = True
