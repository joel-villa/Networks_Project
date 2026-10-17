from abc import ABC, abstractmethod
from meshcore import MeshCore
from ..util.Device import Device

class Test(ABC):
    """Interface for Tests"""

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
