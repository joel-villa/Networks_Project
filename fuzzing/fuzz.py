"""
So this is some randomized input sent to the meshnodes 
"""

from meshcore import EventType, MeshCore
from .user import User
from ..utils.UserType import UserType




class Fuzz:
    """The client handler"""

    device: MeshCore,
    contact: dict,
    seed
    

    def __init__(self, device: MeshCore, contact: dict, seed) -> None:
        self.device = device
        self.contact = contact
        self.seed = seed
        
    

    
    def wuzz(self, iterations:int):
        

    def reply(self, text: str) -> None:
        print(f"Sending: {text}")
        self.device.commands.send_msg(self.contact, text)

    

    async def onMessage(self, event: Event) -> None:
        sender = event.payload["pubkey_prefix"]
        text = event.payload["text"]
        print(f"Message: {text}")
        if sender in self.users:
            print("Sender is already know, let its thread deal with it")
            return