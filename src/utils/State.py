"""An Enum for the known device types"""

from enum import Enum


class State(Enum):
    """state of clients"""

    MENU = 0
    CHOOSING_API = 1
    INITIALIZING = 2
    USER_DECIDING = 3
    RECEIVING_PAGE = 4
