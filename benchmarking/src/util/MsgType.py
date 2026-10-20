"""An enum for the type of the Mesh Node involved in the testing

Resources:
    https://docs.python.org/3/library/enum.html
"""
from enum import auto, StrEnum

class MsgType(StrEnum):
    """Device types"""
    SENDER = auto()
    RECEIVER = auto()
    SETUP_SUCCESS = auto()

    @classmethod
    def _missing_(cls, value):
        value = str(value)
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None
