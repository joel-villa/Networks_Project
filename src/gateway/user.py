"""
User object will be directly interfacing with the user
- Handles the requesting the type of API (API Object)
- And other
- Send state to the gateway
- If multiple results, send the top n article names w/ one sentence
- This is doing all of the querying/section and selection

Added an inbox, as the gateway will recieve the first message, because the client does not know what they are supposed to be listening to
most likely this message with be inocous, such as a hello, but we don't want to miss queries, this way we recive them in
the order in which the mesh recives them
"""

import threading

from meshcore import EventType, MeshCore
from meshcore.events import Event

from ..utils.UserType import UserType


# class syntax
class User:
    """The client handler"""

    device: MeshCore
    contact: dict
    thread: threading.Thread
    first_message:str

    def __init__(self, device: MeshCore, contact: dict, user_type: UserType, first_message:str) -> None:
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
        """
        self.device = device
        self.contact = contact
        self.first_message=first_message
        self.inbox: queue.Queue[str | None] = queue.Queue() #The reason for this is handling them at once, and because the gateway gets the first message
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.inbox.put(first_message)
        self.device.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.handle_message,
            attribute_filters={"pubkey_prefix": contact["public_key"][:12]},
        )

    async def run(self) -> None:
        while True:
            text = self.inbox.get()
            if text is None:
                break
            self.handle_message(text)
        # await self.device.start_auto_message_fetching()
        
        

    async def handle_message(self, recieve_message: Event) -> None:
        raise NotImplementedError

    def destroy(self) -> None:
        self.subscription.unsubscribe()
        self.thread.join()

    def on_message(self, event: Event) -> None:
        self.inbox.put(event.payload["text"])
