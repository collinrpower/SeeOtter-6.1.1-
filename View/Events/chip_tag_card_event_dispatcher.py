from kivy.event import EventDispatcher


class ChipTagCardEventDispatcher(EventDispatcher):

    def __init__(self, **kwargs):
        self.register_event_type('on_tag_pressed')
        super(ChipTagCardEventDispatcher, self).__init__(**kwargs)

    def tag_pressed(self, tag):
        self.dispatch('on_tag_pressed', tag)

    def on_tag_pressed(self, *args):
        pass
