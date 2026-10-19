"""An enum for the type of the Mesh Node involved in the testing

Resources:
    https://docs.python.org/3/library/enum.html
"""
from enum import Enum

# class syntax
class NodeType(Enum):
    SENDER = 1
    RECIEVER = 2
