"""The frame loss test"""

from meshcore import MeshCore
from ...util.Device import Device
from ..Test import Test

class Loss(Test):
    """The latency test class"""


    def __init__(
        self,
        frames_sent: int,
        granularity: float
    ) -> None:
        """Initialize this Loss Test object

        Args:
            max_msgs (int): The maximum messages sent during the latency
        """

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
            source (MeshCore | list[MeshCore]): The devices which are do the
            messaging/timing
            dut (dict): The contact info of the device under test
            srt_type (Device | list[Device]): The device types of the sources
            dst_type (Device): The device type of the dut
            num_frame_sizes (int): The number of frame sizes
            distance (float | list[float]): The distances from the sources to
            the DUT
            notes (str): Anything of note about this test?

        Returns:
             test_id (int): The id of the test
        """
        # Ensure correct input shape
        if type(source) is MeshCore:
            source = [source]
        if type(src_type) is Device:
            src_type = [src_type]
        if type(distance) is float:
            distance = [distance]

        return  -1
