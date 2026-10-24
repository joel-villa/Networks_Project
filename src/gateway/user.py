"""
User object will be directly interfacing with the user
- Handles the requesting the type of API (API Object)
- And other
- Send state to the gateway
- If multiple results, send the top n article names w/ one sentence
- This is doing all of the querying/section and selection
"""

import threading

from meshcore import MeshCore, EventType
from meshcore.events import Event

from SRC.utils.UserType import UserType


# class syntax
class User:
    """The client handler"""

    device: MeshCore
    contact: dict
    thread: threading.Thread

    def __init__(self, device: MeshCore, contact: dict, user_type: UserType) -> None:
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
        """
        self.device = device
        self.contact = contact
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    async def run(self) -> None:
        await self.device.start_auto_message_fetching()
        self.device.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.handle_message,
        )

    async def handle_message(self, recieve_message: Event) -> None:
        raise NotImplementedError

    def destroy(self) -> None:
        raise NotImplementedError
