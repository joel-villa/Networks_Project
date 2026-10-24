"""An Enum for the known device types"""

from enum import Enum


class State(Enum):
    """state of clients"""

    INITIALIZING = 1
    USER_DECIDING = 2
    RECEIVING_PAGE = 3
