"""The device under test (DUT) is expected to have one mesh node, i.e. it
needs a thread and is capable of sending and recieving through that mesh node.
Also, the DUT needs a map of contacts to contacts (contacts to recv and send to
accordingly)"""

import asyncio
from threading import Condition, Thread  # Replace with asyncio.Event
from typing import Any
from warnings import warn

from meshcore import EventType
from meshcore.events import Event
from meshcore.meshcore import MeshCore

from src.loss.util.Handshaker import Handshaker
from src.loss.util.MsgType import MsgType


class DUT:
    """The DUT test class"""

    # Incoming messages are gotten using the public key prefix, outgoing using the contact dict
    dut: MeshCore
    handshaker: Handshaker
    device_map: dict[str, dict[str, Any]]
    done_with_test: asyncio.Event

    def __init__(
        self,
        dut: MeshCore,
    ) -> None:
        self.dut = dut
        self.handshaker = Handshaker()
        self.device_map = {}
        self.done_with_test = asyncio.Event()

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
            await self.dut.commands.send_msg(
                reciever_contact, received_msg.payload["text"]
            )
        else:
            warn(f"No contact associated with pubkey: {sender_prefix}")

        msg_type = MsgType(received_msg.payload["text"])
        match msg_type:
            case MsgType.DONE_WITH_TEST:
                self.done_with_test.set()
            case _:
                pass

    async def run_test(self, n_pairs: int) -> None:
        """Run the loss test on the DUT side of things

        Args:
            n_pairs (int): number of recv+send pairs expected

        Resources:
            - Loop through dictionary key value pairs:
                https://www.w3schools.com/python/python_dictionaries_loop.asp
        """
        await self.handshaker.prep(dut=self.dut, n_pairs=self.n_pairs)
        self.device_map = await self.handshaker.start_dut()

        # The actual loss test
        self.done_with_test.clear()
        self.dut.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.__handle_message,
        )
        await self.dut.start_auto_message_fetching()


    def finish(self) -> None:
        """Wair for the loss test to finish"""
        await self.done_with_test.wait()
        await self.dut.stop_auto_message_fetching()
