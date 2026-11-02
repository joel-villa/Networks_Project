"""
Main Class that will handle most of the server side functionality.
- Contains the clients and will accecpt connections and will spawn new connections
- Will connect users to their desired APIs

- Listen for new connections will create new threads for each client (Client object)
"""

from meshcore import EventType, MeshCore
from .user import User
from ..utils.UserType import UserType


REGEX_THAT_MEANS_COMPUTER = "OwO"


class Gateway:
    """The client handler"""

    device: MeshCore
    users: dict[str, User]

    def __init__(self, device: MeshCore) -> None:
        self.device = device
        self.users = {}

    async def run(self) -> None:
        print("gateway started:")
        self.device.subscribe(EventType.CONTACT_MSG_RECV, self.onMessage)
        await self.device.start_auto_message_fetching()

    async def onMessage(self, event: Event) -> None:
        sender = event.payload["pubkey_prefix"]
        text = event.payload["text"]
        print(f"Message: {text}")
        if sender in self.users:
            print("Sender is already know, let its thread deal with it")
            return

        # so this is so that the thread handles its own message, it will have to pass the first message to the user
        print("looking up contact")
        contact = self.device.get_contact_by_key_prefix(sender)
        if contact is None:
            await self.device.ensure_contacts(follow=True)
            await self.device.start_auto_message_fetching()
            contact = self.device.get_contact_by_key_prefix(sender)
            print("contact none?")
        if contact is None:
            print(f"Message from unknown contact {sender}, ignoring")
            return
        print("Found contact")

        if text == REGEX_THAT_MEANS_COMPUTER:
            user_state = UserType.COMPUTER_USER
            print(f"User said: {text} which means computer")
        else:
            user_state = UserType.BASIC_MESH
            print(f"User said: {text} which means basic mesh")

        print("constructing user")
        self.users[sender] = user = User(self.device, contact, user_state, text)
        print("constructed")
        # print("Attempting to create a new user")
        # self.users[sender] = User(self.device, (self.device.get_contact_by_key_prefix(sender)),UserType.COMPUTER_USER,text)
        # self.users[sender].run()

    def remove_user(self, sender: str) -> None:
        user = self.users.pop(sender, None)
        if user:
            user.destroy()
