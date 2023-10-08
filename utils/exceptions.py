from typing import Optional


class InformationError(Exception):
    def __init__(self, e: Optional[str] = None):
        self.error_description = e

    def __str__(self):
        return f"{self.__class__.__name__} occurred" + (
            f": {self.error_description}" if self.error_description else ""
        )

    def __repr__(self):
        return self.__str__()


class InformationReError(InformationError):
    pass


class InformationRequestError(InformationError):
    pass


class VKAPIRequestError(Exception):
    def __str__(self):
        return "VKAPIRequestError occurred"

    def __repr__(self):
        return self.__str__()
