from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.transparent_icon_button import TransparentIconButton


class SaveButton(TransparentIconButton):

    def __init__(self, controller: SeeOtterControllerBase, callback, **kwargs):
        super().__init__(callback, **kwargs)
        self.controller = controller
        self.icon = "content-save"
        self.bind_events()
        self.on_survey()

    def on_press(self):
        super().on_press()

    def on_unsaved_changes(self, *args):
        has_changes = self.controller.has_unsaved_changes
        if has_changes:
            self.icon = "content-save-outline"
            self.md_bg_color = [1, 1, 1, .2]
        else:
            self.icon = "content-save"
            self.md_bg_color = [0, 0, 0, 0]

    def on_survey(self, *args):
        if self.controller.survey:
            self.disabled = False
        else:
            self.disabled = True

    def bind_events(self):
        self.controller.bind(has_unsaved_changes=self.on_unsaved_changes)
        self.controller.bind(survey=self.on_survey)
