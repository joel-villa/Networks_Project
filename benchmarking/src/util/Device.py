"""An Enum for the known device types

Resources:

"""
from enum import StrEnum, auto


class Device(StrEnum):
    """Device types"""
    HELTEC_V3 = auto()
    HELTEC_T114 = auto()
    SEEED_WIO_TRACKER_L1_PRO = auto()
    NO_DEVICE = auto()

    @classmethod
    def _missing_(cls, value):
        value = str(value)
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None
