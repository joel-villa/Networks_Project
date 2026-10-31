"""The device which handles the initial handshake"""

import sys
from threading import Condition, Lock
from typing import Any
import warnings

from meshcore import EventType, MeshCore
from meshcore.events import Event

from src.loss.util.MsgType import MsgType
from src.util.RDT import RDT
from src.util.constants import N_CHAR_PUB_KEY_PREFIX


class Handshaker:
    """Yktv"""
    device_type: int
    awaiting_done_msg: bool
    cv: Condition
    lock: Lock | None
    rdt: RDT


    def __init__(self, device_type: int) -> None:
        """Initiliaze this handshaker either as the DUT or the time keeper

        Args:
            device_type (int):
                1 -> Time Keeper
                2 -> Device Under Test (DUT)
	    """
        self.device_type = device_type
        self.awaiting_done_msg = False
        self.cv = Condition()
        self.rdt = RDT()
        if device_type == 2: # TODO: SEMAPHORE
            self.lock = Lock()

    def __dut_handshake_msg(
        self,
        received_msg: Event,
        key_to_contact: dict[str, dict],
        recvs:list[str],
        sends:list[dict],
    ) -> None:
        """Handle a message received while doing the handshake

        Args:
            received_msg (Event): The connection message (contains wether
            this device is a SENDER or RECEIVER)

        Resources:
            - Reading messages from the payload with 'text':
                https://pypi.org/project/meshcore/
        """
        assert self.lock is not None, "Huh? Null lock"
        msg_type = MsgType(received_msg.payload["text"])
        receiver_prefix = received_msg.payload["pubkey_prefix"]

        with self.lock:
            match msg_type:
                case MsgType.SENDER:
                    # Test sender => DUT reciever
                    recvs.append(receiver_prefix)
                case MsgType.RECEIVER:
                    # Test receiver => DUT sender
                    contact = key_to_contact.get(receiver_prefix)
                    if contact:
                        sends.append(contact)
                case MsgType.HANDSHAKE_DONE:
                    with self.cv:
                        self.awaiting_done_msg = False
                        self.cv.notify()
                case _:
                    warnings.warn(f"Unexpected MsgType in handshake: {msg_type}")

    async def dut_handshake(
        self,
        dut: MeshCore,
        key_to_contact: dict[str, dict]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        assert self.device_type == 2, f"Handshaker initialized with type f{self.device_type} cannot call this method"
        raise NotImplementedError

    def __handle_msg_from_dut(
        self,
        received_msg: Event,
        dut_key_pref: str,
    ) -> None:
        """Continue the count!

        Args:
            recieved_msg (EventType): Message recieved o7
        """
        print(received_msg.payload["text"])
        sys.stdout.flush()
        if received_msg.payload["pubkey_prefix"] == dut_key_pref:
            with self.cv:
                self.awaiting_done_msg = False
                self.cv.notify()

    async def timekeeper_handshake(
        self,
        devices: list[MeshCore],
        contacts: list[dict[str, Any]],
        timeout_time: float,
    ) -> tuple[list[MeshCore], list[MeshCore], list[dict[str, Any]], list[dict[str, Any]]]:
        """Do tha dang handshake

        Args:
            send_devs (list[MeshCore]): The sending MeshCore devices
            recv_devs (list[MeshCore]): The receiving MeshCore devices
            send_contacts(list[dict]): The contact of the DUT for all senders
            recv_contacts(list[dict]): The contact of the DUT for all receivers
            timeout_time (int): How long to wait for an acknowledgement before
            retrying
        """
        assert self.device_type == 1, f"Handshaker initialized with type f{self.device_type} cannot call this method"
        assert len(devices) == len(contacts), f"Shape mismatch: {len(devices)} != {len(contacts)}"

        self.awaiting_done_msg = True

        n_pairs = len(devices) // 2
        send_devs = devices[:n_pairs]
        recv_devs = devices[n_pairs:]
        send_contacts = contacts[:n_pairs]
        recv_contacts = contacts[n_pairs:]

        odd = len(devices) % 2 != 0
        if odd:
            warnings.warn(f"Odd number of source devices ({len(devices)}), ignoring last")
            recv_devs = recv_devs[:-1]
            recv_contacts = recv_contacts[:-1]

        print("Starting handshake")
        for i, device in enumerate(send_devs):
            await self.rdt.send_msg(
                device=device,
                contact=send_contacts[i],
                message=MsgType.SENDER.name,
                timeout_time=timeout_time,
            )
        for i, device in enumerate(recv_devs):
            await self.rdt.send_msg(
                device=device,
                contact=recv_contacts[i],
                message=MsgType.RECEIVER.name,
                timeout_time=timeout_time,
            )

        for i, device in enumerate(send_devs):
            await self.rdt.send_msg(
                device=device,
                contact=send_contacts[i],
                message=MsgType.HANDSHAKE_DONE.name,
                timeout_time=timeout_time,
            )

        for recv_dev in recv_devs:
            await recv_dev.start_auto_message_fetching()
            recv_dev.subscribe(
                event_type=EventType.CONTACT_MSG_RECV,
                callback=self.__handle_msg_from_dut,  # TODO: handhsake confirmation failing
                attribute_filters={
                    # Only need 12 characters of the dut's pub key to confirm
                    "dut_key_pref": recv_contacts[0]["public_key"][
                        :N_CHAR_PUB_KEY_PREFIX
                    ]
                },
            )

        print("Waiting for handshake to finish")
        with self.cv:
            # Wait for the DUT to setup
            while self.awaiting_done_msg:
                self.cv.wait()

        for recv_dev in recv_devs:
            await recv_dev.stop_auto_message_fetching()

        return send_devs, recv_devs, send_contacts, recv_contacts
