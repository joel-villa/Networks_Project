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
import queue
import asyncio
import traceback
import time

from meshcore import EventType, MeshCore
from meshcore.events import Event

from ..utils.UserType import UserType
from ..utils.State import State
from .Service import Service
from ..utils.Message import Message

MAX_MSG_LEN = 130  # TODO: Check with Joel, see what the best message length is with respect to the latency and loss tests
DELAY = 1.0


# class syntax
class User:
    """The client handler"""

    device: MeshCore
    contact: dict
    thread: threading.Thread
    first_message: str
    service: Service
    user_state: State
    user_type: UserType
    handlers: dict
    current_responce: Any
    responce_index: int

    def __init__(self, device, contact, user_type, first_message):
        """Construct her I hardly know her

        Args:
            device (MeshCore): The device for receiving and sending messages
            contact : The contact of the person that this thread listens for
            user_type : is the user a computer or a mesh end node
            first_message : the gateway is the original listner, thus captures the first message, so this has to be passed in
        """
        print("attempting to construct")

        self.device = device
        self.contact = contact
        self.user_type = user_type
        self.current_responce = "Please query an API first"

        self.service = Service(
            user_type
        )  # this will break silently if you dont have the secrets.jon, ask Joel or Natalie

        self.user_state = State.MENU
        self.current_api = ""

        self.loop = asyncio.get_running_loop()
        self.inbox = queue.Queue()
        # print("Not the loop or que")

        self.handlers = {  # Manages users by the state that they are in
            State.MENU: self.handle_menu,
            State.CHOOSING_API: self.handle_choosing_api,
            State.INITIALIZING: self.handle_query,
            State.RECEIVING_PAGE: self.continue_serving,
        }

        self.inbox.put(first_message)

        self.thread = threading.Thread(target=self.run, daemon=True)

        self.thread.start()
        self.subscription = device.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.on_message,
            attribute_filters={"pubkey_prefix": contact["public_key"][:12]},
        )

    def run(self) -> None:
        """Loops forever, swallows exceptions so that a bad api call doesn't break the thread"""
        while True:
            text = self.inbox.get()
            if text is None:
                break
            print(f"Received: {text}")
            try:
                self.handle_message(text)
            except Exception as e:
                print(e)

    def handle_message(self, text: str) -> None:
        """Sends the message off to the appropriate handler, depending on user state

        Args:
            self: This User instance
            text: The message sent by the user
        """
        handler = self.handlers[self.user_state]
        handler(text)

    def handle_menu(self, text: str) -> None:
        """Prints the avalible services form the service instance

        Args:
            self: This User instance
            text: The message sent by the user
        """
        self.user_state = State.CHOOSING_API
        self.reply(self.service.available_services())

    def handle_choosing_api(self, text: str) -> None:
        """Sets the users choosen API

        Args:
            self: This User instance
            text: The message sent by the user, hopefully an api name
        """
        name = text.strip().lower()
        if name not in self.service.func_dict:
            self.reply("Unknown service. " + self.service.available_services())
            return
        self.current_api = name
        self.reply("Please send me: " + " ".join(self.service.get_params(name)))
        self.user_state = State.INITIALIZING

    # TODO: This method need to be rewriten with respect to the differences between the user types
    def handle_query(self, text: str) -> None:
        """Querys the API

        Args:
            self: This User instance
            text: The query sent by the user
        """
        result = self.service.call_api(self.current_api, text)
        self.current_responce = str(result)
        self.user_state = State.RECEIVING_PAGE
        if self.user_type is UserType.BASIC_MESH:
            self.start_serving_mesh()
            return
        self.start_serving_computer()

    def start_serving_mesh(self):
        self.reply("To continue: type any letter, to stop type : menu or stop or exit")
        first_chunk = self.current_responce[:MAX_MSG_LEN]
        self.responce_index = 1
        self.reply(first_chunk)

    # def start_serving_computer(self):
    #     """Creates the message to be sent to the computer user

    #     Args:
    #         self: This User instance
    #     """
    #     message = Message(current_responce,uuid.uuid4().int, 0, (len(current_responce)/MAX_MSG_LEN))
    #     i=0
    #     final_sequence_number = (len(current_responce)/MAX_MSG_LEN)-1
    #     package_id =uuid.uuid4().int

    #     while(i is not final_sequence_number):
    #         current_starter = i *MAX_MSG_LEN
    #         nextChunk = self.current_responce[current_starter:current_starter+MAX_MSG_LEN]

    #         message = Message((current_responce), package_id, i, (len(current_responce)/MAX_MSG_LEN))

    def start_serving_computer(self):
        i = 0
        final_sequence_number = (len(self.current_responce) / MAX_MSG_LEN) - 1

        while i is not final_sequence_number:
            current_starter = i * MAX_MSG_LEN
            nextChunk = self.current_responce[
                current_starter : current_starter + MAX_MSG_LEN
            ]
            self.reply(nextChunk)
            i += 1
            time.sleep(DELAY)

    def continue_serving(self, text: str):
        """Prints the message one chunk at a time, this is intended for mesh users

        Args:
            self: This User instance
            text: The message sent by the user
        """
        if text.lower() in ("menu", "stop", "exit"):
            self.user_state = State.MENU
            return

        # something something index * message size to get next chunk
        current_starter = self.responce_index * MAX_MSG_LEN
        nextChunk = self.current_responce[
            current_starter : current_starter + MAX_MSG_LEN
        ]
        self.reply(nextChunk)
        self.responce_index += 1

    def destroy(self) -> None:
        self.subscription.unsubscribe()
        self.thread.join()

    async def on_message(self, event: Event) -> None:
        self.inbox.put(event.payload["text"])

    def reply(self, text: str) -> None:
        print(f"Sending: {text}")
        future = asyncio.run_coroutine_threadsafe(
            self.device.commands.send_msg(self.contact, text), self.loop
        )
        future.result(timeout=30)
