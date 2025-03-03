from kivy.graphics import Rectangle


def set_background_color(widget, color):
    with widget.canvas:
        widget.canvas.clear()
        Rectangle(size=widget.size, pos=widget.pos, color=color)


def get_kivy_coordinates(coordinates, resolution):
    x, y = coordinates
    width, height = resolution
    return x, height-y


def get_standard_image_coordinates(coordinates, resolution):
    x, y = coordinates
    width, height = resolution
    return x, height-y


def switch_scene(obj, scene, direction="left", duration=.5):
    manager = obj.manager
    if manager.current != scene:
        transition = manager.transition
        transition.direction = direction
        transition.duration = duration
        manager.current = scene
