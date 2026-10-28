"""The Test Super Class"""

from abc import ABC, abstractmethod
from time import perf_counter

import numpy as np
from meshcore import EventType, MeshCore

from .util.Device import Device


class Test(ABC):
    """Interface for Tests"""

    num_rtts: int = 5  # How many rtts to do when rtt_time() is called
    prop_min_time: float = (
        0.9  # What proportion of the minimum rtt is considered small enough
    )
    prop_max_time: float = (
        2.0  # What proportion of the maximum rtt is considered small enough
    )
    max_timeout: float = 10  # The maximum timeout on lost mesage possible

    def get_frame_sizes(self, num_frame_sizes: int) -> np.ndarray:
        """Get the frame sizes from teh number of frame sizes

        Args:
            num_frame_sizese (int): The number of frame sizes

        Returns:
             frame_sizes (np.ndarray): Those frame sizes to test
        """
        return np.linspace(
            start=1,  # Sending message of minimum size 1
            stop=150,
            num=num_frame_sizes,
            dtype=int,
        )

    async def round_trip_time(
        self,
        meshcore: MeshCore,
        dst_key: dict,
        message: str,
        timeout: float = 5,  # TODO: expose this to top level API + add to metadata tracker
    ) -> float:
        """Time a message's ACK

        Args:
            meshcore (MeshCore): The sending device
            dst_key (dict): The contact of the device under test
            message (str): The message to send

        Returns:
            rtt (float): The time elapsed from message sent and ACK recieved
        """
        start = perf_counter()
        # Send the message and get information about the sent message
        sent_result = await meshcore.commands.send_msg(dst_key, message)

        # Extract the expected acknowledgment code from the message sent event
        if sent_result.type == EventType.ERROR:
            return np.nan

        expected_ack = sent_result.payload["expected_ack"].hex()

        # Wait specifically for this acknowledgment
        result = await meshcore.wait_for_event(
            EventType.ACK, attribute_filters={"code": expected_ack}, timeout=timeout
        )
        stop = perf_counter()

        if result:
            return stop - start
        else:
            # Timeout -> NaN
            return np.nan

    async def rtt_time(
        self,
        source: MeshCore | list[MeshCore],
        dut: dict | list[dict],
        frame_sizes: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Find the minimum and maximum rtt for the given frame sizes

        Args:
            source (MeshCore | list[MeshCore]): The sending device(s)
            dut (list[dict]): Contact info of device under test for each device
            frame_sizezss (np.ndarray): The frame_sizes

        Returns:
             min_rtt (np.ndarray): The minimum round trip time per frame size
             max_rtt (np.ndarray): The maximum round trip time per frame size
        """
        # Ensure stuff is correct shape
        if type(source) is MeshCore:
            source = [source]
        if type(dut) is dict:
            dut = [dut]

        min_rtt = np.full((frame_sizes.shape[0],), self.max_timeout)
        max_rtt = np.zeros((frame_sizes.shape[0],))

        for i, frame_size in enumerate(frame_sizes):
            message = "a"
            message *= frame_size
            for j, meshcore in enumerate(source):
                for k in range(self.num_rtts):
                    rtt_time = await self.round_trip_time(
                        meshcore=meshcore,
                        dst_key=dut[j],
                        message=message,
                        timeout=self.max_timeout,  # TODO: expose this to top level API + add to metadata tracker
                    )

                    min_rtt[i] = min(min_rtt[i], rtt_time)
                    max_rtt[i] = max(max_rtt[i], rtt_time)

        return min_rtt, max_rtt

    async def get_contacts(
        self,
        local_devices: MeshCore | list[MeshCore],
        dut_name: str,
    ) -> dict | list[dict]:
        """Get the contacts for each local device

        Args:
            local_device (MeshCore | list[MeshCore]): The local devices
            dut_name (str): The name of the contact

        Returns:
             dut_contacts (dict | list[dict]): The contacts of the dut for each
             device
        """
        was_list = type(local_devices) is list
        if not was_list:
            local_devices = [local_devices]

        dut_contacts = []
        for device in local_devices:
            print(f"source_dev: {device}")
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

        assert len(local_devices) == len(dut_contacts), (
            f"Source device does not have DUT in contacts: {dut_contacts}"
        )

        if was_list:
            return dut_contacts
        return dut_contacts[0]

    @abstractmethod
    async def run_test(
        self,
        source: MeshCore | list[MeshCore],
        dut_name: str,
        src_type: Device | list[Device],
        dst_type: Device,
        num_frame_sizes: int,
        distance: float | list[float] | None,
        notes: str | None,
    ) -> int:
        """Run the test

        Args:
            source (list[Meshcore]): The devices which are do the messaging/
            timing
            dut (dict): The contact info of the device under test
            srt_type (list[Device]): The device types of the sources
            dst_type (Device): The device type of the dut
            num_frame_sizes (int): The number of frame sizes
            distance (list[float]): The distances from the sources to the DUT
            notes (str): Anything of note about this test?

        Returns:
             test_id (int): The id of the test
        """
