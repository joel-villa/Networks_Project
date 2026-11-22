"""Ohhh, that good benchmarking"""

import asyncio
import os

from dotenv import load_dotenv

from src.DistanceTracker import DistanceTracker
from src.latency.Latency import Latency
from src.latency.LatencyResults import LatencyResults
from src.loss.Loss import Loss
from src.loss.LossResults import LossResults
from src.loss.Receiver import MeshCore
from src.util.Device import Device


async def main_loss(
    source: list[MeshCore],
    name_under_test: str,
    distance: list[float],
    source_type: list[Device],
    dst_type: Device,
) -> None:
    frame_count = 16
    granularity = 0.1  # 0.1 is maximum granularity
    num_frame_sizes = 1  # 5 is minimum
    prop_min_time = 7 / 16  # 1/2 is latency 7/8 * 1/2 = 7/16
    prop_max_time = 1.5
    n_rtts = 5
    max_time = 2  # Max timeout time (seconds)
    # Connect to your device

    loss_test = Loss(
        frames_sent=frame_count,
        granularity=granularity,
        prop_min_time=prop_min_time,
        prop_max_time=prop_max_time,
        num_rtts=n_rtts,
        max_timeout=max_time,
    )

    handshake_result = await loss_test.run_handshake(
        source=source,
        dut_name=name_under_test,
    )
    file_id = await loss_test.run_test(
        handshake_result=handshake_result,
        src_type=source_type,
        dst_type=dst_type,
        num_frame_sizes=num_frame_sizes,
        distance=distance,
        notes="testing thangs",
    )

    results = LossResults(file_name=file_id)
    results.disp_results()


async def main_latency(
    meshcore: MeshCore,
    name_under_test: str,
    distance: float,
    src_type: Device,
    dst_type: Device,
) -> None:
    # TODO: get this test to under 5 minutes for scaling to larger tests
    num_frame_sizes = 5  # 5 at minimum
    max_msgs = 32
    max_time = 600  # 30 mins = 1800 seconds, 5 mins = 300 seconds, 4 mins = 260 seconds
    notes = None

    lat_test = Latency(
        max_msgs=max_msgs,  # Max message per framesize
        max_time=max_time,  # Max time of entire test
    )

    file_id = await lat_test.run_test(
        source=meshcore,
        dut_name=name_under_test,
        src_type=src_type,
        dst_type=dst_type,
        num_frame_sizes=num_frame_sizes,
        distance=distance,
        notes=notes,
    )

    results = LatencyResults(file_name=file_id)
    results.disp_results()


async def main() -> None:
    """Run the test purposes"""
    load_dotenv()
    path_0 = os.getenv("MESH_PATH")
    path_1 = os.getenv("MESH_PATH_1")
    assert path_0 is not None
    assert path_1 is not None

    name_under_test = "pro_0"

    print("Connecting devices")
    meshcore_0 = await MeshCore.create_serial(path_0)
    meshcore_1 = await MeshCore.create_serial(path_1)
    meshcores = [
        meshcore_0,
        meshcore_1,
    ]
    src_types = [
        Device.HELTEC_T114,
        Device.HELTEC_T114,
    ]
    dst_type = Device.SEEED_WIO_TRACKER_L1_PRO

    # Check contact path is one hop
    for i, mesh in enumerate(meshcores):
        result = await mesh.commands.get_contacts()
        contacts = result.payload
        if contacts:
            for contact in contacts.values():
                if contact["adv_name"] == name_under_test:
                    assert contact["out_path"] == "", (
                        f"Not zero hop, out_path: {contact['out_path']}"
                    )
                    print(
                        f"Contact Path {i}: {contact['out_path']} (type: {type(contact['out_path'])})"
                    )

    distances = []
    for mesh in meshcores:
        dist_tracker = DistanceTracker(
            src_dev=mesh,
        )
        dist = await dist_tracker.measure_dist(
            dest_device=name_under_test,
        )
        distances.append(dist)
        print(f"Distance between mesh and DUT: {dist}")

    # print("Running Latency Test!")
    # await main_latency(
    #    meshcore=meshcores[0],
    #    name_under_test=name_under_test,
    #    distance=distances[0],
    #    src_type=src_types[0],
    #    dst_type=dst_type,
    # )

    print("Running Loss Test!")
    await main_loss(
        source=meshcores,
        name_under_test=name_under_test,
        distance=distances,
        source_type=src_types,
        dst_type=dst_type,
    )

    await meshcore_0.disconnect()
    await meshcore_1.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
