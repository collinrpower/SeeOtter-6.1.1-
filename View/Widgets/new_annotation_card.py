from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.stack_card import StackCard


class NewAnnotationCard(StackCard):
    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__("Add Annotation", **kwargs)
        self.controller = controller
