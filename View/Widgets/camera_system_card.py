import os
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey import Survey
from View.Widgets.camera_card import CameraCard
from View.Widgets.property_stack_card import PropertyStackCard


class CameraSystemCard(PropertyStackCard):

    tabs = None
    camera_cards = []

    def __init__(self, controller: SeeOtterControllerBase, title, **kwargs):
        super().__init__(controller, title, **kwargs)
        self.height = 590

    def build(self):
        self.add_header_button(text="Open Camera Config", callback=self.open_camera_system_config)
        self.tabs = TabbedPanel(do_default_tab=False, background_color=(1, 1, 1, 0))
        self.tabs.bind(size=self.resize_tabs)

    def build_cards(self):
        if self.controller.survey and self.controller.survey.camera_system:
            self.tabs.clear_tabs()
            self.layout.remove_widget(self.tabs)
            self.add(self.tabs)
            camera_system = self.controller.survey.camera_system
            for camera in camera_system.cameras:
                panel = TabbedPanelHeader(text=camera.name, background_color=(.7, .7, .7, .8))
                panel.content = CameraCard(title=f"Camera: {camera.name}", controller=self.controller, camera=camera)
                self.tabs.add_widget(panel)
            if len(self.tabs.tab_list) > 0:
                self.tabs.switch_to(self.tabs.tab_list[-1])

    def resize_tabs(self, *args):
        num_tabs = len(self.tabs.tab_list)
        if num_tabs > 0:
            self.tabs.tab_width = self.tabs.width / num_tabs

    def clear_fields(self):
        super().clear_fields()
        self.layout.remove_widget(self.tabs)

    def set_fields(self, survey: Survey):
        camera_system = survey.camera_system
        self.clear_fields()
        self.title = f"Camera System: {camera_system.name}" if camera_system else "No Camera System"
        self.build_cards()

    def open_camera_system_config(self, *args):
        if self.controller.survey:
            os.startfile(self.controller.survey.camera_system_path)
