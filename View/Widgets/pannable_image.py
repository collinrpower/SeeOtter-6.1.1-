import PIL
import kivy
from os.path import exists
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, StencilPush, StencilUse, StencilUnUse, StencilPop, Ellipse
from Utilities.kivy_utilities import get_kivy_coordinates, get_standard_image_coordinates
from Utilities.utilities import get_root_path
from View.Events.pannable_image_event_dispatcher import PannableImageEventDispatcher

kivy.require("1.9.1")


class PannableImage(Widget):

    min_zoom = 0.05
    max_zoom = 20.0
    zoom_in_factor = .75
    zoom_out_factor = 1.25
    background_image = get_root_path("View/Images/OtterCheckerBackground1.jpg")

    def __init__(self, **kwargs):
        super(PannableImage, self).__init__(**kwargs)

        # Default Vars
        self.resolution = (-1, -1)
        self.aspect_ratio = 0
        self.zoom_level = 1.0
        self.mouse_click_offset = (0, 0)
        self.image = None
        self.image_path = None
        self.is_dragging = False
        self.disable_panning = False

        # Initialization
        self.event = PannableImageEventDispatcher()
        self.apply_background_image()
        self.bind_events()

    @property
    def current_image_is_background(self):
        return self.image_path == self.background_image

    def update_mask(self, *kwargs):
        with self.canvas:
            self.canvas.clear()
            Color(.2, .2, .2, 1)
            # Background
            Rectangle(size=self.size, pos=self.pos)
            StencilPush()
            mask = Rectangle(size=self.size, pos=self.pos)
            StencilUse()
            Color(1, 1, 1, 1)  # set the colour
            self.canvas.add(self.image)
            StencilUnUse()
            self.canvas.add(mask)
            StencilPop()

    def bind_events(self):
        self.event.bind(on_image_changed=self.refresh_actual_zoom_level)
        self.bind(size=self.update_mask)

    def set_image(self, path):
        print("Set Image")
        self.image_path = path
        self.resolution = self.get_resolution(self.image_path)
        self.image = Rectangle(source=path, size_hint=(None, None), size=self.resolution)
        self.aspect_ratio = self.image.size[0] / self.image.size[1]
        if self.current_image_is_background:
            self.stretch_image()
        else:
            self.fit_image()
        self.update_mask()

    def apply_background_image(self):
        self.set_image(self.background_image)
        self.stretch_image()

    def limit_image_pos(self):
        img_x, img_y = self.image.pos
        img_width, img_height = self.image.size
        panel_x, panel_y = self.pos
        panel_width, panel_height = self.size
        left, bottom = img_x, img_y
        top = bottom + img_height
        right = left + img_width

        # Rectangle is narrower than panel
        if img_width < panel_width:
            if left < panel_x:
                img_x = panel_x
            if right > panel_x + panel_width:
                img_x = panel_x + panel_width - img_width

        # Rectangle is taller than panel
        if img_height < panel_height:
            if bottom < panel_y:
                img_y = panel_y
            if top > panel_y + panel_height:
                img_y = panel_y + panel_height - img_height

        self.image.pos = (img_x, img_y)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if touch.is_mouse_scrolling:
            self.zoom_on_mouse_scroll(touch)
        elif touch.button == "left":
            self.handle_left_mouse_click(touch)
        elif touch.button == "right":
            pass
        else:
            print(f"Unrecognized mouse button: {touch.button}")
        Widget.on_touch_down(self, touch)

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        if touch.button == "left":
            self.handle_left_mouse_drag(touch)

    def handle_left_mouse_drag(self, touch):
        if self.is_dragging:
            self.image.pos = (touch.pos[0] + self.mouse_click_offset[0], touch.pos[1] + self.mouse_click_offset[1])
            self.limit_image_pos()
            self.image_moved(None)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.button == "left":
            self.handle_left_mouse_release(touch)

    def handle_left_mouse_release(self, touch):
        self.is_dragging = False

    def handle_left_mouse_click(self, touch):
        self.get_pixel_coordinates_at_pos(touch.pos)
        if self.collide_point(*touch.pos) and not self.disable_panning:
            self.mouse_click_offset = self.mouse_image_offset(touch.pos)
            self.is_dragging = True
        else:
            self.is_dragging = False

    def zoom_on_mouse_scroll(self, touch):
        if touch.button == 'scrolldown':
            self.zoom_out(touch.pos)
        elif touch.button == 'scrollup':
            self.zoom_in(touch.pos)

    def zoom_in(self, mouse_pos):
        self.zoom(zoom_gain=self.zoom_in_factor, target_pos=mouse_pos)

    def zoom_out(self, mouse_pos):
        self.zoom(zoom_gain=self.zoom_out_factor, target_pos=mouse_pos)

    def apply_zoom_gain(self, zoom_gain):
        next_zoom_level = self.zoom_level * zoom_gain
        if next_zoom_level < self.min_zoom or next_zoom_level > self.max_zoom:
            return
        else:
            self.set_zoom_level(next_zoom_level)

    def refresh_actual_zoom_level(self, *args):
        actual_zoom = self.image.size[0] / self.resolution[0]
        if actual_zoom > self.max_zoom:
            self.set_zoom_level(self.max_zoom)
        elif actual_zoom < self.min_zoom:
            self.set_zoom_level(self.min_zoom)
        else:
            self.set_zoom_level(actual_zoom)

    def set_zoom_level(self, zoom_level):
        previous_zoom_level = self.zoom_level
        if zoom_level != previous_zoom_level:
            self.zoom_level = zoom_level
            self.event.zoom_level_changed(self.zoom_level)

    def get_target_size_pos(self, target_pos, zoom):
        image_target_offset = self.multiply_position(target_pos, zoom)
        viewport_center_offset = self.width/2, self.height/2
        size = self.multiply_position(self.resolution, zoom)
        pos = self.subtract_position(self.pos, image_target_offset)
        pos = self.add_position(pos, viewport_center_offset)
        return size, pos

    def zoom(self, target_pos, zoom_gain=None, zoom_level=None, animation_duration=0):
        if not (zoom_level or zoom_gain):
            raise Exception("Zoom method requires either zoom_gain or zoom_level as arguments.")
        mouse_offset = self.mouse_image_offset(target_pos)
        scaled_mouse_offset = self.multiply_position(mouse_offset, zoom_gain)
        initial_zoom = self.zoom_level
        self.apply_zoom_gain(zoom_gain)
        # Scale and move image if zoom has changed
        if initial_zoom != self.zoom_level:
            size = (self.resolution[0] * self.zoom_level, self.resolution[1] * self.zoom_level)
            pos = self.add_position(target_pos, scaled_mouse_offset)
            if animation_duration == 0:
                self.image.size = size
                self.image.pos = pos
                self.event.image_changed()
            else:
                anim = Animation(pos=pos, size=size, duration=animation_duration)
                anim.on_progress = self.on_animation_progress
                anim.start(self.image)

    def pan_to_standard_coords(self, pos, zoom_level=None, duration=None):
        kivy_coords = get_kivy_coordinates(pos, self.resolution)
        self.pan_to(kivy_coords, zoom_level, duration)

    def pan_to(self, pos, zoom_level=None, duration=0):
        new_size, new_pos = self.get_target_size_pos(pos, zoom_level)
        if duration == 0:
            self.image.size = new_size
            self.image.pos = new_pos
            self.event.image_changed()
        else:
            pan_animation = Animation(pos=new_pos, size=new_size, duration=duration)
            pan_animation.on_progress = self.on_animation_progress
            pan_animation.start(self.image)

    def mouse_image_offset(self, mouse_pos):
        return self.subtract_position(self.image.pos, mouse_pos)

    def animate(self, duration=1, **kwargs):
        anim = Animation(duration=duration, **kwargs)
        anim.on_progress = self.on_animation_progress
        anim.start(self.image)

    def fit_image(self, duration=0, *kwargs):
        print("Fit Image")
        width, height = self.size[0], self.size[1]
        panel_aspect_ratio = self.size[0] / self.size[1]
        if panel_aspect_ratio > self.aspect_ratio:
            width = height * self.aspect_ratio
        else:
            height = width / self.aspect_ratio
        if duration == 0:
            self.image.size = (width, height)
            self.center_image()
            self.event.image_changed()
        else:
            self.animate(size=(width, height), pos=self.pos)

    def center_image(self, *kwargs):
        print("Center Image")
        widget_center = self.get_center(self)
        image_center = self.get_center(self.image)
        offset = self.subtract_position(widget_center, image_center)
        self.image.pos = self.add_position(self.image.pos, offset)
        self.refresh_actual_zoom_level()
        self.event.image_changed()

    def stretch_image(self, duration=0, on_complete=None, *kwargs):
        print("Stretch Image")
        duration = duration if isinstance(duration, float) else 0
        anim = Animation(pos=self.pos, size=self.size, duration=duration)
        anim.on_progress = self.on_animation_progress
        if on_complete:
            anim.on_complete = on_complete
        anim.start(self.image)

    def on_animation_progress(self, *args):
        percent_progress = args[1] * 100
        self.event.image_changed()

    def get_pixel_coordinates_at_pos(self, pos):
        pos_diff = self.subtract_position(pos, self.image.pos)
        pixel_coords = self.divide_position(pos_diff, self.zoom_level)
        standard_coords = get_standard_image_coordinates(pixel_coords, resolution=self.resolution)
        return standard_coords

    @staticmethod
    def get_resolution(path):
        img = PIL.Image.open(path)
        return img.size

    @staticmethod
    def subtract_position(pos1, pos2):
        return pos1[0] - pos2[0], pos1[1] - pos2[1]

    @staticmethod
    def add_position(pos1, pos2):
        return pos1[0] + pos2[0], pos1[1] + pos2[1]

    @staticmethod
    def multiply_position(pos, number):
        return pos[0] * number, pos[1] * number

    @staticmethod
    def divide_position(pos, number):
        return pos[0] / number, pos[1] / number

    @staticmethod
    def get_center(element):
        return PannableImage.add_position(element.pos, (element.size[0] / 2, element.size[1] / 2))


class CanvasApp(App):
    def build(self):
        return PannableImage()
