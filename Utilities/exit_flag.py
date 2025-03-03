
class ExitFlag:

    def __init__(self):
        self.is_raised = False

    def __bool__(self):
        return self.is_raised

    def request_exit(self):
        self.is_raised = True

    def reset(self):
        self.is_raised = False
