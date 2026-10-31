"""
Main Class that will handle most of the server side functionality.
- Contains the clients and will accecpt connections and will spawn new connections
- Will connect users to their desired APIs

- Listen for new connections will create new threads for each client (Client object)
"""

from meshcore import EventType, MeshCore


class Gateway:
    """The client handler"""

    device: MeshCore
    users: dict[str, user]

    def __init__(self, device: MeshCore) -> None:
        self.device = device
        self.users ={}


    async def run(self) -> None:
        self.device.subscribe(EventType.CONTACT_MSG_RECV, self.onMessage)
        await self.device.start_auto_message_fetching()

    def onMessage(self, event:Event)-> None:
        sender = event.payload["pubkey_prefix"]
        text = event.payload["text"]
        if sender in self.users:
            return
        
        #so this is so that the thread handles its own message

        self.users[sender] = user(self.device, (self.device.get_contact_by_key_prefix(sender)),UserType.COMPUTER_USER,text)

