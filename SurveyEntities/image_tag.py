

class ImageTag:

    def __init__(self, name, description=None, state=False):
        self.name = name
        self.description = description
        self.state = state

    def __repr__(self):
        return f"Tag: {self.name}"
