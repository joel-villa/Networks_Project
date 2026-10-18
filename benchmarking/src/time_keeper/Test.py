"""The Test Super Class"""
import numpy as np
from abc import ABC, abstractmethod
from meshcore import MeshCore
from ..util.Device import Device

class Test(ABC):
    """Interface for Tests"""

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
        dut: dict,
        num_msgs: int,
        frame_sizes: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Find the minimum and maximum rtt for the given frame sizes

        Args:
            source (MeshCore | list[MeshCore]): The sending device(s)
            dut (dict): Contact info of device under test
            num_msgs (int): Number of messages to base rtt on
            frame_sizezss (np.ndarray): The frame_sizes

        Returns:
             min_rtt (np.ndarray): The minimum round trip time per frame size
             max_rtt (np.ndarray): The maximum round trip time per frame size
        """
        pass

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
