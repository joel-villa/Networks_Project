"""Message me up Scotty!"""

from .UserType import UserType

MAX_MSG_LEN = 130
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
        # sequence_number: int,
        # final_sequence_number: int,
    ) -> None:
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
        """
        self.message = message
        self.id =id
        self.sequence_number = 0
        self.final_sequence_number = message/MAX_MSG_LEN

    def to_string(self) -> str:
        return f"{id}:{sequence_number}:message"
    
    def get_next_message(self) -> Any:
        if(self.sequence_number is not self.final_sequence_number):
            return None
        current_starter = self.sequence_number * MAX_MSG_LEN
        nextChunk = self.current_responce[
                current_starter : current_starter + MAX_MSG_LEN
            ]
        message = f"{id}:{sequence_number}:{nextChunk}"
        self.sequence_number+=1
        return message

        
