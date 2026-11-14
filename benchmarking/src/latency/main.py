
import asyncio
import os

from dotenv import load_dotenv
from meshcore import MeshCore

from src.latency.Latency import Latency
from src.latency.LatencyResults import LatencyResults
from src.util.Device import Device


async def main():
    """Run the test purposes"""
    load_dotenv()
    path_to_dev = os.getenv("MESH_PATH")
    assert path_to_dev is not None

    file_id = 2

    contact_under_test = "SenseCap_Solar_0"

    # TODO: get this test to under 5 minutes for scaling to larger tests
    num_frame_sizes = 8  # 5 at minimum
    max_msgs = 1024
    max_time = 1800 # 30 mins = 1800 seconds
    src_type = Device.SEEED_WIO_TRACKER_L1_PRO
    dst_type = Device.SEEED_SENSECAP_SOLAR
    distance = None
    notes = None

    meshcore = await MeshCore.create_serial(path_to_dev)

    file_id = -1

    lat_test = Latency(
        max_msgs=max_msgs,
        max_time=max_time,
    )

    file_id = await lat_test.run_test(
        source=meshcore,
        dut_name=contact_under_test,
        src_type=src_type,
        dst_type=dst_type,
        num_frame_sizes=num_frame_sizes,
        distance=distance,
        notes=notes,
    )

    await meshcore.disconnect()

    results = LatencyResults(file_name=file_id)
    results.disp_results()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
