"""The device under test (DUT) is expected to have one mesh node, i.e. it
needs a thread and is capable of sending and recieving through that mesh node.
Also, the DUT needs a map of contacts to contacts (contacts to recv and send to
accordingly)"""

import asyncio
from threading import Condition
from typing import Any
from warnings import warn

from meshcore import EventType
from meshcore.events import Event
from meshcore.meshcore import MeshCore

from src.loss.util.Handshaker import Handshaker
from src.loss.util.MsgType import MsgType
from src.util.constants import N_CHAR_PUB_KEY_PREFIX


class DUT:
    """The DUT test class"""

    # Incoming messages are gotten using the public key prefix, outgoing using the contact dict
    dut: MeshCore
    handshaker: Handshaker
    device_map: dict[str, dict[str, Any]]
    awaiting_done_msg: bool
    cv: Condition

    def __init__(
        self,
        dut: MeshCore,
    ) -> None:
        self.dut = dut
        self.handshaker = Handshaker(device_type=2)
        self.device_map = {}
        self.awaiting_done_msg = False
        self.cv = Condition()
        asyncio.run(self.__init_dut())


    async def __init_dut(self) -> None:
        """You know the vibes, put the asynchronous stuff here (including
        handshake)
        Resources:
            - Loop through dictionary key value pairs:
                https://www.w3schools.com/python/python_dictionaries_loop.asp
        """
        key_to_contact = {}

        result = await self.dut.commands.get_contacts()
        contacts = result.payload
        if contacts:
            for pub_key, contact in contacts.items():
                pub_key_pref = pub_key[:N_CHAR_PUB_KEY_PREFIX]
                key_to_contact[pub_key_pref] = contact
        else:
            raise ValueError("device under test contacts inaccessible")
        self.device_map = await self.handshaker.dut_handshake(dut=self.dut, key_to_contact=key_to_contact)

    async def __handle_message(
        self,
        received_msg: Event,
    ) -> None:
        """Handle a message from a sender, update the receiver

        Args:
            received_msg (Event): The message recieved by this device
        """
        sender_prefix = received_msg.payload["pubkey_prefix"]
        reciever_contact = self.device_map.get(sender_prefix)

        if reciever_contact:
            await self.dut.commands.send_msg(reciever_contact, received_msg.payload['text'])
        else:
            warn(f"No contact associated with pubkey: {sender_prefix}")

        msg_type = MsgType(received_msg.payload["text"])
        match msg_type:
            case MsgType.DONE_WITH_TEST:
                with self.cv:
                    self.awaiting_done_msg = False
                    self.cv.notify()
            case _:
                pass

    async def run_test(self) -> None:
        self.awaiting_done_msg = True
        await self.dut.start_auto_message_fetching()
        self.dut.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.__handle_message,
        )

        while self.awaiting_done_msg:
            with self.cv:
                self.cv.wait()
        await self.dut.stop_auto_message_fetching()
