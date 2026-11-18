"""Message me up Scotty!"""

from .UserType import UserType
from math import ceil
from typing import Any

MAX_MSG_LEN = 130
MAX_HEADER_LEN =20
#print(len("こんにちは".encode("utf-8"))) is 15 bytes even though its just 5 chars
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
        self.final_sequence_number = ceil(len(message)/MAX_MSG_LEN)


    def to_string(self) -> str:
        return f"Packet id: {self.id} Expect: {self.final_sequence_number}"
    

    def build_message(self) ->  str:
        current_starter = self.sequence_number * MAX_MSG_LEN
        print(f"Sequence number: {self.sequence_number}, Current starter: {current_starter}")
        nextChunk = self.message[
                current_starter : current_starter + MAX_MSG_LEN
        ]
        return nextChunk

    def build_header(self) -> str:
        header = f"{self.id}:{self.sequence_number}:"
        
        return header

    def get_next_message(self) -> Any:
        if(self.sequence_number >= self.final_sequence_number):
            return None
        message = self.build_header() + self.build_message()
        self.sequence_number+=1
        return message

        
