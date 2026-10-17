"""The latency test class"""

import asyncio
from meshcore import MeshCore

from ..results.LatencyResults import LatencyResults
from ..tests.latency import get_latencies
from ..util.Device import Device
from .Test import Test


class Latency(Test):
    """The latency test class"""

    max_msgs: int
    max_time: int

    def __init__(
        self,
        max_msgs: int,
        max_time: int,
    ) -> None:
        """Initialize this Latency Test object

        Args:
            max_msgs (int): The maximum messages sent during the latency
            test
            max_time (int): The maximum time the latency test runs per
            frame size (in seconds)
        """
        self.max_msgs = max_msgs
        self.max_time = max_time

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
        assert type(source) is MeshCore, f"{type(source)}"
        assert type(src_type) is Device, f"{type(src_type)}"
        assert type(distance) is float or distance is None, f"{type(distance)}"

        print("Starting test")
        frame_sizes, latencies = await get_latencies(
            meshcore=source,
            dst_key=dut,
            num_frame_sizes=num_frame_sizes,
            max_msgs=self.max_msgs,
            max_time=self.max_time // num_frame_sizes,
        )

        results = LatencyResults(
            src_type=src_type,
            dst_type=dst_type,
            distance=distance,
            num_frame_sizes=num_frame_sizes,
            max_msgs=self.max_msgs,
            max_time=self.max_time,
            notes=notes,
            frame_sizes=frame_sizes,
            latencies=latencies,
        )
        file_name = results.save_results()

        return file_name


async def wrap_run_test(
    contact_under_test: str,
    num_frame_sizes: int,
    max_msgs: int,
    max_time: int,
    src_type: Device,
    dst_type: Device,
    distance: float | None,
    notes: str | None,
) -> int:
    """Wrapper for run_test()

    Args:
        contact_under_test (str): the string of the contact to test
        num_frame_sizes (int): The number of frame sizes tested
        max_msgs (int): The maximum number of messages sent during
        test of a given frame size
        max_time (int): The maxium time of test (seconds) for a given
        frame size
        src_type (Device): The type of the timing device
        dst_type (Device): The type of the Device Under Test
        distance (float | None): The distance between the src and dst
        notes (str | None): Anything to note?

    Returns:
         file_num (int): file number the test is saved under
    """
    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")

    # Get your contacts
    result = await meshcore.commands.get_contacts()
    contacts = result.payload

    file_id = -1

    # Send a message to T114-j
    if contacts:
        for contact in contacts.values():
            if contact["adv_name"] == contact_under_test:
                lat_test = Latency(
                    max_msgs=max_msgs,
                    max_time=max_time,
                )

                file_id = await lat_test.run_test(
                    source=meshcore,
                    dut=contact,
                    src_type=src_type,
                    dst_type=dst_type,
                    num_frame_sizes=num_frame_sizes,
                    distance=distance,
                    notes=notes,
                )

    await meshcore.disconnect()

    return file_id


async def main():
    """Main for testing purposes"""
    contact_under_test = "T114_0"

    # TODO: get this test to under 5 minutes for scaling to larger tests
    num_frame_sizes = 8  # 5 at minimum
    max_msgs = 1024
    max_time = 260
    src_type = Device.HELTEC_V3
    dst_type = Device.HELTEC_T114
    distance = None
    notes = None

    file_id = 2

#    file_id = await wrap_run_test(
#        contact_under_test=contact_under_test,
#        num_frame_sizes=num_frame_sizes,
#        max_msgs=max_msgs,
#        max_time=max_time,
#        src_type=src_type,
#        dst_type=dst_type,
#        distance=distance,
#        notes=notes,
#    )

    results = LatencyResults(file_name=file_id)
    results.disp_results()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
