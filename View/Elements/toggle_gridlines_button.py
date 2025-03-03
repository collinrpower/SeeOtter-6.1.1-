from Controller.see_otter_controller_base import SeeOtterControllerBase
from View.Elements.transparent_icon_button import TransparentIconButton


class ToggleGridlinesButton(TransparentIconButton):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__(callback=self.button_pressed, tooltip="Toggle Gridlines", size_hint_x=None, width=60, **kwargs)
        self.controller = controller
        self.update_icon()

    def button_pressed(self, *args):
        self.controller.gridlines_visible = not self.controller.gridlines_visible
        self.update_icon()

    def update_icon(self):
        if self.controller.gridlines_visible:
            self.icon = "grid"
        else:
            self.icon = "grid-off"
