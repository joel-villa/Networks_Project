"""Tracks the distance between two mesh nodes"""

import asyncio
from functools import partial
from warnings import warn
from geopy import distance

from asyncio.coroutines import os
from dotenv import load_dotenv
from meshcore import EventType, MeshCore
from meshcore.events import Event

from src.loss.Receiver import N_CHAR_PUB_KEY_PREFIX


class DistanceTracker:
    """Distance tracker, I hardly know her..

    Resources:
        - Finding distance between two gps coordinates (lat, lon)
            https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    """
    _src_dev: MeshCore
    _src_loc: tuple[float, float]
    _dut_loc: tuple[float, float]
    _coords_received: asyncio.Event

    def __init__(
        self,
        src_dev: MeshCore,
    ) -> None:
        """Initialize this distance tracker

        Args:
            src_dev (MeshCore): The device currently connected
	    """
        self._src_dev = src_dev
        self._src_loc = (0, 0)
        self._dut_loc = (0, 0)
        self._coords_received = asyncio.Event()

    async def __set_src_loc(self) -> None:
        """Set the source coordinates"""
        self_info = await self._src_dev.commands.send_appstart()
        src_lat = self_info.payload['adv_lat']
        src_lon = self_info.payload['adv_lon']
        self._src_loc = (src_lat, src_lon)

    @property
    async def src_loc(self) -> tuple[float, float]:
        """A getter for the source location

        Returns:
             src_loc (tuple[float, float]): source's coordinates
        Resources:
            - Read only properties in python:
                https://www.pythonmorsels.com/making-read-only-attribute/
	    """
        await self.__set_src_loc()
        return self._src_loc


    def __distance_in_meters(self) -> float:
        """Distance in meteres of two GPS locations (lat, long)

        Args:
            fst_loc (tuple[float, float]): The first latitude longitude tuple
            snd_loc (tuple[float, float]): The second latitude longitude tuple

        Returns:
             distance (float): Distance between teh two locations in meters
	    """
        if self._src_loc == (0, 0):
            warn(f"Source location is null island: {self._src_loc}")
        if self._dut_loc == (0, 0):
            warn(f"Source location is null island: {self._dut_loc}")
        print(f"src_loc: {self._src_loc}, dst_loc: {self._dut_loc}")
        return distance.distance(self._src_loc, self._dut_loc).meters


    async def __recv_msg(
        self,
        received_msg: Event,
        dut_pubkey: str,
    ) -> None:
        """ receiving that dang message

        Args:
            recieved_msg (EventType): Message recieved o7
            pubkey (str): The public key of the DUT
        """
        received_key = received_msg.payload["public_key"]

        if received_key != dut_pubkey:
            return

        result = await self._src_dev.commands.get_contacts()
        contacts = result.payload
        contact = contacts.get(dut_pubkey)

        if contact is None:
            warn("Contact not found")
            return

        lat = contact.get("adv_lat")
        lon = contact.get("adv_lon")

        if lat is None or lon is None:
            warn("No location included in advertisement")
            return

        self._dut_loc = (lat, lon)
        self._coords_received.set()

    async def measure_dist(self, dest_device: str, timeout: float = 10) -> float:
        """Measure the distance between a device and one of its contacts

        Args:
            dest_device (str): The contact name of the device to get the
            distance to
            timeout (float): How long to wait until failure

        Returns:
             distance (float): Distance between the devices (in meters)
	    """
        # Get contact
        await self._src_dev.start_auto_message_fetching()
        result = await self._src_dev.commands.get_contacts()
        contacts = result.payload
        dest_contact = None
        if contacts:
            for contact in contacts.values():
                if contact["adv_name"] == dest_device:
                    dest_contact = contact

        assert dest_contact is not None, f"{dest_device} not in contacts"

        # Handling an adertisement message type from dut
        callback_func = partial(
            self.__recv_msg,
            dut_pubkey=dest_contact['public_key'],
        )
        subscription = self._src_dev.subscribe(
            event_type=EventType.ADVERTISEMENT,
            callback=callback_func,
        )

        print(f"In DistanceTracker, waiting for coordinate advert from {dest_device}")
        # Wait for the coordinates to be set
        await self._coords_received.wait()

        await self.__set_src_loc()

        await self._src_dev.stop_auto_message_fetching()
        self._src_dev.unsubscribe(subscription)

        return self.__distance_in_meters()

async def main():
    """For testing purposes"""
    load_dotenv()
    path_to_dev = os.getenv("MESH_PATH")
    assert path_to_dev is not None

    contact_under_test = "pro_0"

    meshcore = await MeshCore.create_serial(path_to_dev)

    dist_tracker = DistanceTracker(
        src_dev=meshcore,
    )
    print(f"src_loc: {await dist_tracker.src_loc}")
    dist = await dist_tracker.measure_dist(
        dest_device=contact_under_test,
    )
    print(f"dist:{dist}")

    await meshcore.disconnect()

if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
