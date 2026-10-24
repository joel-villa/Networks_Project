""" """

from SRC.utils.UserType import UserType


class Message:
    user_type: UserType
    message: str
    id: int
    sequence_number: int
    final_sequence_number: int

    def __init__(
        self,
        user_type: UserType,
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
        raise NotImplementedError
