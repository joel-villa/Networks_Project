"""The device under test (DUT) is expected to have one mesh node, i.e. it
needs a thread and is capable of sending and recieving through that mesh node.
Also, the DUT needs a map of contacts to contacts (contacts to recv and send to
accordingly)"""

import asyncio
from warnings import warn

from meshcore.events import Event
from meshcore.meshcore import MeshCore

from src.loss.util.MsgType import MsgType
from src.util.constants import N_CHAR_PUB_KEY_PREFIX


class DUT:
    """The DUT test class"""

    # Incoming messages are gotten using the public key prefix, outgoing using the contact dict
    recvs: list[str]
    sends: list[dict]
    dut: MeshCore
    key_to_contact: dict[str, dict]

    def __init__(
        self,
        dut: MeshCore,
    ) -> None:
        self.dut = dut
        self.recvs = []
        self.sends = []
        asyncio.run(self.__init_dut())

    async def __init_dut(self) -> None:
        """You know the vibes, put the asynchronous stuff here (including
        handshake)
        Resources:
            - Loop through dictionary key value pairs:
                https://www.w3schools.com/python/python_dictionaries_loop.asp
        """
        result = await self.dut.commands.get_contacts()
        contacts = result.payload
        if contacts:
            for pub_key, contact in contacts.items():
                pub_key_pref = pub_key[:N_CHAR_PUB_KEY_PREFIX]
                self.key_to_contact[pub_key_pref] = contact
        else:
            raise ValueError("device under test contacts inaccessible")
        await self.dut.start_auto_message_fetching()
        self.__handshake()

    def __handshake(self) -> None:
        raise NotImplementedError

    def __handle_message(
        self,
        received_msg: Event,
    ) -> None:
        """Handle a message from a sender, update the receiver

        Args:
            received_msg (Event): The message recieved by this device
        """
        raise NotImplementedError

    def __handshake_msg(
        self,
        received_msg: Event,
    ) -> None:
        """Handle a message received while doing the handshake

        Args:
            received_msg (Event): The connection message (contains wether
            this device is a SENDER or RECEIVER)

        Resources:
            - Reading messages from the payload with 'text':
                https://pypi.org/project/meshcore/
        """
        msg_type = MsgType(received_msg.payload['text'])
        receiver_prefix = received_msg.payload['pubkey_prefix']

        match msg_type:
            case MsgType.SENDER:
                # Test sender => DUT reciever
                self.recvs.append(receiver_prefix)
            case MsgType.RECEIVER:
                # Test receiver => DUT sender
                contact = self.key_to_contact.get(receiver_prefix)
                if contact:
                    self.sends.append(contact)
            case MsgType.
            case _:
                warn(f"Unexpected MsgType in handshake: {msg_type}")


    async def destroy(self) -> None:
        """Do all the termination things: delete threads, stop expecting
        messages, etc.
        """
        await self.dut.stop_auto_message_fetching()
