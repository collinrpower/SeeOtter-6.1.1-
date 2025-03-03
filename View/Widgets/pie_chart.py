from kivy.graphics import Ellipse, Color, Rectangle
from kivy.vector import Vector
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from random import random
from math import atan2, sqrt, pow, degrees, sin, cos, radians


class PieChart(GridLayout):
    def __init__(self, data, position, size, legend_enable=True, **kwargs):
        super(PieChart, self).__init__(**kwargs)

        # main layout parameters
        self.position = position
        self.size_mine = size
        self.col_default_width = 100
        self.data = {}
        self.cols = 2
        self.rows = 1
        self.col_force_default = True
        self.col_default_width = 200
        self.row_force_default = True
        self.row_default_height = 200
        self.size_hint_y = None
        self.size = (400, 450)
        self.temp = []

        for key, value in data.items():
            if type(value) is int:
                percentage = (value / float(sum(data.values())) * 100)
                color = [random(), random(), random(), 1]
                self.data[key] = [value, percentage, color]

            elif type(value) is tuple:
                vals = []
                for l in data.values():
                    vals.append(l[0])
                percentage = (value[0] / float(sum(vals)) * 100)
                color = value[1]
                self.data[key] = [value[0], percentage, color]

        self.pie = Pie(self.data, self.position, self.size_mine)
        self.add_widget(self.pie)

        if legend_enable:
            self.legend = LegendTree(self.data, self.position, self.size_mine)
            self.add_widget(self.legend)

        self.bind(size=self._update_pie, pos=self._update_pie)

        # yellow background to check widgets size and position
        # with self.canvas:
        #    Rectangle(pos=self.pos, size=self.size, color=Color(1, 1, 0, 0.5))

    def _update_pie(self, instance, value):
        self.legend.pos = (instance.parent.pos[0], instance.parent.pos[1])
        self.pie.pos = (instance.pos[0], instance.pos[1])


class LegendTree(GridLayout):
    def __init__(self, data, position, size, **kwargs):
        super(LegendTree, self).__init__(**kwargs)

        # Legend layout parameters.
        # Initial rows is 1, then for each next data entry new one is added.
        self.cols = 1
        self.rows = 1
        self.position = position
        self.size = size
        self.row_default_height = 50
        self.spacing = 5

        count = 0
        for key, value in data.items():
            percentage = value[1]
            color = value[2]
            # add legend (rectangle and text)
            self.legend = Legend(pos=(self.position[0], self.position[1] - count * self.size[1] * 0.15),
                                 size=self.size,
                                 color=color,
                                 name=key,
                                 value=percentage)
            self.add_widget(self.legend)
            self.rows += 1
            count += 1

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.legend.pos = (instance.parent.pos[0], instance.parent.pos[1])
        self.pos = (instance.parent.pos[0] + 260, instance.parent.pos[1])


# Class for creating Legend
class Legend(FloatLayout):
    def __init__(self, pos, size, color, name, value, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 1
        self.size_hint_x = 200
        self.size_hint_y = 50
        self.name = name
        with self.canvas.before:
            Color(*color)
            self.rect = Rectangle(pos=(pos[0] + size[0] * 1.3, pos[1] + size[1] * 0.9),
                                  size=(size[0] * 0.1, size[1] * 0.1))
            self.label = Label(text=str("%.2f" % value + "% - " + name),
                               pos=(pos[0] + size[0] * 1.3 + size[0] * 0.5, pos[1] + size[1] * 0.9 - 30),
                               halign='left',
                               text_size=(size[1], size[1] * 0.1))

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = (instance.pos[0] + 50, instance.pos[1] + 50)
        self.label.pos = (instance.pos[0] + 150, instance.pos[1] + 10)


class Pie(FloatLayout):
    def __init__(self, data, position, size, **kwargs):
        super(Pie, self).__init__(**kwargs)
        self.position = position
        self.size = size
        angle_start = 0
        count = 0
        self.temp = []
        for key, value in data.items():
            percentage = value[1]
            angle_end = angle_start + 3.6 * percentage
            color = value[2]
            # add part of Pie
            self.temp.append(PieSlice(pos=self.position, size=self.size,
                                      angle_start=angle_start,
                                      angle_end=angle_end, color=color, name=key))
            self.add_widget(self.temp[count])
            angle_start = angle_end
            count += 1
        self.bind(size=self._update_temp, pos=self._update_temp)

    def _update_temp(self, instance, value):
        for i in self.temp:
            i.pos = (instance.parent.pos[0] + 55, instance.parent.pos[1] + 60)


# Class for making one part of Pie
# Main functions for handling move out/in and click inside area recognition
class PieSlice(FloatLayout):
    def __init__(self, pos, color, size, angle_start, angle_end, name, **kwargs):
        super(PieSlice, self).__init__(**kwargs)
        self.moved = False
        self.angle = 0
        self.name = name
        with self.canvas.before:
            Color(*color)
            self.slice = Ellipse(pos=pos, size=size,
                                 angle_start=angle_start,
                                 angle_end=angle_end)
        self.bind(size=self._update_slice, pos=self._update_slice)

    def _update_slice(self, instance, value):
        self.slice.pos = (instance.pos[0], instance.pos[1])
