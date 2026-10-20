"""The Test Super Class"""
import numpy as np
from abc import ABC, abstractmethod
from time import perf_counter
from meshcore import MeshCore
from ..util.Device import Device

class Test(ABC):
    """Interface for Tests"""
    num_rtts: int = 5 # How many rtts to do when rtt_time() is called
    prop_min_time: float = 0.9 # What proportion of the minimum rtt is considered small enough
    prop_max_time: float = 2.0 # What proportion of the maximum rtt is considered small enough

    def get_frame_sizes(self, num_frame_sizes: int) -> np.ndarray:
        """Get the frame sizes from teh number of frame sizes

        Args:
            num_frame_sizese (int): The number of frame sizes

        Returns:
             frame_sizes (np.ndarray): Those frame sizes to test
        """
        return np.linspace(
            start=1, # Sending message of minimum size 1
            stop=150,
            num=num_frame_sizes,
            dtype=int
        )

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

        min_rtt = np.full((frame_sizes.shape[0],), np.inf)
        max_rtt = np.zeros((frame_sizes.shape[0],))

        for i, frame_size in enumerate(frame_sizes):
            message = 'a'
            message *= frame_size
            for j, meshcore in enumerate(source):
                for k in range(self.num_rtts):
                    start = perf_counter()
                    await meshcore.commands.send_msg(dut[j], message)
                    stop = perf_counter()

                    rtt_time = stop - start

                    min_rtt[i] = min(min_rtt[i], rtt_time)
                    max_rtt[i] = max(max_rtt[i], rtt_time)

        return min_rtt, max_rtt

    @abstractmethod
    async def run_test(
        self,
        source: MeshCore | list[MeshCore],
        dut: dict,
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
