
class SeeOtterException(Exception):
    pass


class ImageDirNotFoundException(SeeOtterException):
    pass


class SurveyDirNotFoundException(SeeOtterException):
    pass


class SurveyVersionException(SeeOtterException):
    pass


class NoCameraSystemException(SeeOtterException):
    pass
