"""Message me up Scotty!"""

from .UserType import UserType


# Due to the fact that meshnodes should recives slower and that for users, it would be confusing to add an id an message numbers
# I think we should just use this for the computer
class Message:
    message: str
    id: int
    sequence_number: int
    final_sequence_number: int

    def __init__(
        self,
        message: str,
        id: int,
        sequence_number: int,
        final_sequence_number: int,
    ) -> None:
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
        """
        self.user_type = user_type
        self.message = message
        self.id = id
        self.sequence_number = sequence_number
        self.final_sequence_number = final_sequence_number

    def to_string(self) -> str:
        return f"{id}:{sequence_number}:message"
