from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from Config.otter_checker_config import OtterCheckerConfig

Builder.load_string("""
<BorderedGridCell>:
    canvas:
        Color:
            rgba: self.border_color
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)
""")


class BorderedGridCell(Button):

    border_color = ListProperty(OtterCheckerConfig.instance().GRIDLINE_COLOR)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)


class GridLines(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize_grid()

    def redraw(self, image):
        self.size = image.size
        self.pos = image.pos

    def initialize_grid(self):
        self.cols = OtterCheckerConfig.instance().GRID_COLUMNS
        self.remove_child_cells()
        self.create_child_cells()

    def remove_child_cells(self):
        for child in [c for c in self.children]:
            self.remove_widget(child)

    def create_child_cells(self):
        rows = OtterCheckerConfig.instance().GRID_ROWS
        cols = OtterCheckerConfig.instance().GRID_COLUMNS
        while len(self.children) < rows * cols:
            self.add_widget(BorderedGridCell())

    @staticmethod
    def normalized_img_size(val, resolution):
        return val[0] / resolution[0], val[1] / resolution[1]
