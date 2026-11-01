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
from ..utils.State import State
from Service import Service


# class syntax
class User:
    """The client handler"""

    device: MeshCore
    contact: dict
    thread: threading.Thread
    first_message:str
    service:Service
    user_state:State

    def __init__(self, device: MeshCore, contact: dict, user_type: UserType, first_message:str) -> None:
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
        """
        self.device = device
        self.contact = contact
        self.first_message=first_message
        self.current_api =""
        self.inbox: queue.Queue[str | None] = queue.Queue() #The reason for this is handling them at once, and because the gateway gets the first message
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.inbox.put(first_message)
        self.user_state = State.MENU
        self._handlers = {
            State.MENU: self.handle_menu,
            State.CHOOSING_API: self.handle_choosing_api,
            State.INITIALIZING: self.handle_query,
        }
        self.device.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.handle_message,
            attribute_filters={"pubkey_prefix": contact["public_key"][:12]},
        )
        self.service = Service()

    async def run(self) -> None:
        while True:
            text = self.inbox.get()
            if text is None:
                break
            self.handle_message(text)
        # await self.device.start_auto_message_fetching()
        



    #     # raise NotImplementedError
    async def handle_message(self, text: str) -> None:
        handler = self._handlers[self.user_state]
        await handler(text)

    async def handle_menu(self, text: str) -> None:
        await self.reply(self.service.available_services())
        self.user_state = State.CHOOSING_API

    async def handle_choosing_api(self, text: str) -> None:
        name = text.strip().lower()
        if name not in self.service.func_dict:
            await self.reply("Unknown service. " + self.service.available_services())
            return 
        self.current_api = name
        await self.reply("Send: " + " ".join(self.service.get_params(name)))
        self.user_state = State.INITIALIZING

    async def handle_query(self, text: str) -> None:
        result = self.service.call_api(self.current_api, text)
        await self.reply(str(result))
        self.user_state = State.MENU


    def destroy(self) -> None:
        self.subscription.unsubscribe()
        self.thread.join()

    def on_message(self, event: Event) -> None:
        self.inbox.put(event.payload["text"])

    def reply(self, text: str) -> None:
        self.device.commands.send_msg(self.contact, text)
