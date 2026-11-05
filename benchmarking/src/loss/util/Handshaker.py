"""The device which handles the initial handshake

Resources:
    - Events (an asynchronous condition variable):
        https://docs.python.org/3/library/asyncio-sync.html#asyncio.Event
"""

import asyncio
import os
import sys
import warnings
from functools import partial
from threading import BoundedSemaphore  # TODO: replace with event
from typing import Any

from dotenv import load_dotenv
from meshcore import EventType, MeshCore
from meshcore.events import Event, Subscription

from src.loss.util.MsgType import MsgType
from src.util.constants import N_CHAR_PUB_KEY_PREFIX
from src.util.RDT import RDT


class Handshaker:
    """Yktv"""

    handshake_done: asyncio.Event
    rdt: RDT
    subscriptions: list[tuple[MeshCore, Subscription]]

    # DUT stuffs
    senders: list[str]
    receivers: list[dict[str, Any]]
    send_semaphore: BoundedSemaphore
    recv_semaphore: BoundedSemaphore

    def __init__(self) -> None:
        """Initiliaze this handshaker either as the DUT or the time keeper"""
        self.handshake_done = asyncio.Event()
        self.rdt = RDT()
        self.subscriptions = []
        # NOTE: not assigning DUT class variables here (assigned in dut_handshek())

    def __usnubscribe(self):
        for device, subscription in self.subscriptions:
            device.unsubscribe(subscription)
        self.subscriptions = []

    async def __dut_handshake_msg(
        self,
        received_msg: Event,
        n_pairs: int,
        key_to_contact: dict[str, dict],
    ) -> None:
        """Handle a message received while doing the handshake

        Args:
            received_msg (Event): The connection message (contains wether
            this device is a SENDER or RECEIVER)
            key_to_contact (dict[str, dict]): Maps public keys to contacts

        Resources:
            - Reading messages from the payload with 'text':
                https://pypi.org/project/meshcore/
        """
        msg_type = MsgType(received_msg.payload["text"])
        print(f"in __dut_handshake_msg: {msg_type}")
        sys.stdout.flush()
        pubkey_prefix = received_msg.payload["pubkey_prefix"]
        print(f"pubkey_prefix: {pubkey_prefix}")
        sys.stdout.flush()

        match msg_type:
            case MsgType.SENDER:
                with self.send_semaphore:
                    self.senders.append(pubkey_prefix)
            case MsgType.RECEIVER:
                contact = key_to_contact.get(pubkey_prefix)
                if contact:
                    with self.recv_semaphore:
                        self.receivers.append(contact)
            case _:
                warnings.warn(f"Unexpected MsgType in handshake: {msg_type}")
        if len(self.receivers) == n_pairs and len(self.senders) == n_pairs:
            # DONE WITH HANDSHAKE!
            self.handshake_done.set()

    async def start_dut(
        self,
        dut: MeshCore,
        n_pairs: int,
    ) -> None:
        """The device under test calls this method to do the handshake, it will
        return when complete

        Args:
            dut (MeshCore): The MeshCore object
            n_pairs (int): Expected number of send and recv pairs

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
        # Setting key_to_contact dict via a handshake
        key_to_contact = {}

        result = await dut.commands.get_contacts()
        contacts = result.payload
        if contacts:
            for pub_key, contact in contacts.items():
                pub_key_pref = pub_key[:N_CHAR_PUB_KEY_PREFIX]
                key_to_contact[pub_key_pref] = contact
        else:
            raise ValueError("device under test contacts inaccessible")

        self.receivers = []
        self.senders = []
        self.recv_semaphore = BoundedSemaphore(value=1)
        self.send_semaphore = BoundedSemaphore(value=1)

        callback_func = partial(
            self.__dut_handshake_msg,
            n_pairs=n_pairs,
            key_to_contact=key_to_contact,
        )
        subscription = dut.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=callback_func,
        )
        self.subscriptions.append((dut, subscription))
        self.handshake_done.clear()
        await dut.start_auto_message_fetching()

    async def finish_dut(self, dut: MeshCore) -> dict[str, dict[str, Any]]:
        """Wait for the handshake to finish

        Args:
            dut (MeshCore): Finish the DUT handshake

        Returns:
             name (type): Description
        """
        print("DUT: Waiting for Handshake to finish")
        sys.stdout.flush()

        await self.handshake_done.wait()
        self.__usnubscribe()
        await dut.stop_auto_message_fetching()

        # Ensure all processing is good to go
        with self.recv_semaphore:
            pass
        with self.send_semaphore:
            pass

        device_map = {}
        for i, sender in enumerate(self.senders):
            device_map[sender] = self.receivers[i]

        print("DUT: alerting receivers that the handshake is done")
        sys.stdout.flush()
        for receiver in device_map.values():
            await dut.commands.send_msg(
                receiver,
                MsgType.HANDSHAKE_DONE.name,
            )

        return device_map

    async def __handle_msg_from_dut(
        self,
        received_msg: Event,
        dut_key_pref: str,
    ) -> None:
        """Continue the count!

        Args:
            recieved_msg (EventType): Message recieved o7
            dut_key_pref (str): The dut public key prefix
        """
        print(f"in __handle_msg_from_dut: {received_msg.payload['text']}")
        sys.stdout.flush()
        if received_msg.payload["pubkey_prefix"] == dut_key_pref:
            self.handshake_done.set()

    async def start_timekeeper(
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
        assert len(devices) == len(contacts), (
            f"Shape mismatch: {len(devices)} != {len(contacts)}"
        )
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

        self.handshake_done.clear()

        # When receive done message -> done
        callback_func = partial(
            self.__handle_msg_from_dut,
            dut_key_pref=recv_contacts[0]["public_key"][:N_CHAR_PUB_KEY_PREFIX],
        )
        for recv_dev in recv_devs:
            await recv_dev.start_auto_message_fetching()
            subscription = recv_dev.subscribe(
                event_type=EventType.CONTACT_MSG_RECV,
                callback=callback_func,
            )
            self.subscriptions.append((recv_dev, subscription))

        print("TimeKeeper: Starting handshake")
        sys.stdout.flush()
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

        return send_devs, recv_devs, send_contacts, recv_contacts

    async def finish_timekeeper(self, recv_devs: list[MeshCore]) -> None:
        print("TimeKeeper: Waiting for handshake to finish")
        sys.stdout.flush()
        # Wait for the DUT to setup
        await self.handshake_done.wait()
        self.__usnubscribe()

        for recv_dev in recv_devs:
            await recv_dev.stop_auto_message_fetching()


async def main() -> None:
    """Run a loss test"""

    load_dotenv()
    # bluetooth = os.getenv("BLUETOOTH")
    # bluetooth_pin = os.getenv("BLE_PIN")
    path_0 = os.getenv("MESH_PATH")
    path_1 = os.getenv("MESH_PATH_1")
    path_2 = os.getenv("MESH_PATH_2")
    # assert bluetooth is not None
    # assert bluetooth_pin is not None
    assert path_0 is not None
    assert path_1 is not None
    assert path_2 is not None

    print("Connecting devices")
    sys.stdout.flush()
    # Connect to your device
    #    dut_mesh = await MeshCore.create_ble(bluetooth, pin=bluetooth_pin)
    send_mesh = await MeshCore.create_serial(path_0)
    recv_mesh = await MeshCore.create_serial(path_1)
    dut_mesh = await MeshCore.create_serial(path_2)

    handshake_timekeeper = Handshaker()
    handshake_dut = Handshaker()

    dut_name = "pro_0"
    local_devices = [send_mesh, recv_mesh]
    dut_contacts = []
    for device in local_devices:
        if device is None:
            raise ValueError(f"None source: {local_devices}")
        # Get your contacts
        result = await device.commands.get_contacts()
        contacts = result.payload
        if contacts:
            for contact in contacts.values():
                #                    print(f"contact: {contact}")
                if contact["adv_name"] == dut_name:
                    dut_contacts.append(contact)
                    break

    await handshake_dut.start_dut(
        dut=dut_mesh,
        n_pairs=len(local_devices) // 2,
    )
    (
        send_devs,
        recv_devs,
        send_contacts,
        recv_contacts,
    ) = await handshake_timekeeper.start_timekeeper(
        devices=local_devices,
        contacts=dut_contacts,
        timeout_time=5,
    )
    device_map = await handshake_dut.finish_dut(dut=dut_mesh)
    await handshake_timekeeper.finish_timekeeper(recv_devs=recv_devs)

    print(
        f"send_devs:{send_devs}, recv_devs:{recv_devs}, send_contacts: {send_contacts}, recv_contacts: {recv_contacts}\ndevice_map:{device_map}"
    )


if __name__ == "__main__":
    """Python main"""
    asyncio.run(main())
