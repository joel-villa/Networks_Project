"""The device which handles the initial handshake"""

import sys
import warnings
from functools import partial
from threading import BoundedSemaphore, Condition
from typing import Any

from meshcore import EventType, MeshCore
from meshcore.events import Event

from src.loss.util.MsgType import MsgType
from src.util.constants import N_CHAR_PUB_KEY_PREFIX
from src.util.RDT import RDT


class Handshaker:
    """Yktv"""

    device_type: int
    awaiting_done_msg: bool
    cv: Condition
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

    def __dut_handshake_msg(
        self,
        received_msg: Event,
        key_to_contact: dict[str, dict],
        receivers: list[str],
        senders: list[dict],
        recv_semaphore: BoundedSemaphore,
        send_semaphore: BoundedSemaphore,
    ) -> None:
        """Handle a message received while doing the handshake

        Args:
            received_msg (Event): The connection message (contains wether
            this device is a SENDER or RECEIVER)

        Resources:
            - Reading messages from the payload with 'text':
                https://pypi.org/project/meshcore/
        """
        msg_type = MsgType(received_msg.payload["text"])
        pubkey_prefix = received_msg.payload["pubkey_prefix"]

        match msg_type:
            case MsgType.SENDER:
                # Test sender => DUT reciever
                contact = key_to_contact.get(pubkey_prefix)
                if contact:
                    with send_semaphore:
                        senders.append(contact)
            case MsgType.RECEIVER:
                with recv_semaphore:
                    receivers.append(pubkey_prefix)
            case MsgType.HANDSHAKE_DONE:
                with self.cv:
                    self.awaiting_done_msg = False
                    self.cv.notify()
            case _:
                warnings.warn(f"Unexpected MsgType in handshake: {msg_type}")

    async def dut_handshake(
        self, dut: MeshCore, key_to_contact: dict[str, dict]
    ) -> dict[str, dict[str, Any]]:
        """The device under test calls this method to do the handshake, it will
        return when complete

        Args:
            dut (MeshCore): The MeshCore object
            key_to_contact (dict[str, dict]): A dictionary of public key
            prefixes to contact dictionary object

        Returns:
            device_map (dict[str, dict[str, Any]]): A map of sending device
            public key prefixes to receiving device contacts (from timekeeper
            perspective)

        Resources:
            - Empyt list check:
                https://www.geeksforgeeks.org/python/python-check-if-list-empty-not/
            - Semaphores:
                https://docs.python.org/3/library/threading.html
            - Partial Functions:
                https://docs.python.org/3/library/functools.html
        """
        assert self.device_type == 2, (
            f"Handshaker initialized with type f{self.device_type} cannot call this method"
        )

        receivers = []
        senders = []
        recv_semaphore = BoundedSemaphore(value=1)
        send_semaphore = BoundedSemaphore(value=1)

        await dut.start_auto_message_fetching()
        callback_func = partial(
            self.__dut_handshake_msg,
            key_to_contact=key_to_contact,
            receivers=receivers,
            senders=senders,
            recv_semaphore=recv_semaphore,
            send_semaphore=send_semaphore,
        )
        dut.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=callback_func,
        )

        while self.awaiting_done_msg:
            with self.cv:
                self.cv.wait()

        # Ensure all processing is good to go
        with recv_semaphore:
            pass
        with send_semaphore:
            pass

        if not receivers or not senders:
            raise ValueError(
                f"handshake failed: num recievers is {len(receivers)}, num senders is {len(senders)}"
            )

        if len(receivers) != len(senders):
            min_count = min(len(receivers), len(senders))
            warnings.warn(
                f"recieved unequal number of recievers ({len(receivers)}) and senders ({len(senders)}), reducing both to {min_count}"
            )
            receivers = receivers[:min_count]
            senders = senders[:min_count]

        device_map = {}
        for i, sender in enumerate(senders):
            device_map[sender] = receivers[i]

        return device_map

    def __handle_msg_from_dut(
        self,
        received_msg: Event,
        dut_key_pref: str,
    ) -> None:
        """Continue the count!

        Args:
            recieved_msg (EventType): Message recieved o7
            dut_key_pref (str): The dut public key prefix
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
    ) -> tuple[
        list[MeshCore], list[MeshCore], list[dict[str, Any]], list[dict[str, Any]]
    ]:
        """Do tha dang handshake

        Args:
            devices (list[MeshCore]): the devices to do the handshake with
            contacts (list[dict[str, Any]]): The contact of the dut for each
            device
            timeout_time (int): How long to wait for an acknowledgement before
            retrying

        Return:
            send_devs (list[MeshCore]): The sending MeshCore devices
            recv_devs (list[MeshCore]): The receiving MeshCore devices
            send_contacts(list[dict]): The contact of the DUT for all senders
            recv_contacts(list[dict]): The contact of the DUT for all receivers
        """
        assert self.device_type == 1, (
            f"Handshaker initialized with type f{self.device_type} cannot call this method"
        )
        assert len(devices) == len(contacts), (
            f"Shape mismatch: {len(devices)} != {len(contacts)}"
        )

        self.awaiting_done_msg = True

        n_pairs = len(devices) // 2
        send_devs = devices[:n_pairs]
        recv_devs = devices[n_pairs:]
        send_contacts = contacts[:n_pairs]
        recv_contacts = contacts[n_pairs:]

        odd = len(devices) % 2 != 0
        if odd:
            warnings.warn(
                f"Odd number of source devices ({len(devices)}), ignoring last"
            )
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

        callback_func = partial(
            self.__handle_msg_from_dut,
            dut_key_pref=recv_contacts[0]["public_key"][:N_CHAR_PUB_KEY_PREFIX],
        )
        for recv_dev in recv_devs:
            await recv_dev.start_auto_message_fetching()
            recv_dev.subscribe(
                event_type=EventType.CONTACT_MSG_RECV,
                callback=callback_func,
            )

        print("Waiting for handshake to finish")
        # Wait for the DUT to setup
        while self.awaiting_done_msg:
            with self.cv:
                self.cv.wait()

        for recv_dev in recv_devs:
            await recv_dev.stop_auto_message_fetching()

        return send_devs, recv_devs, send_contacts, recv_contacts
