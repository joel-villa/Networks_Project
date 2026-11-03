"""For running the loss tests all on one machine"""

import asyncio
import os

from dotenv import load_dotenv
from meshcore import MeshCore

from src.loss.DUT import DUT
from src.loss.Loss import Loss
from src.loss.LossResults import LossResults
from src.util.Device import Device


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

    contact_under_test = "pro_0"
    frame_count = 5
    granularity = 0.1  # 10% is maximum granularity
    num_frame_sizes = 5  # 5 is minimum
    prop_min_time = 0.9
    prop_max_time = 2
    n_rtts = 3
    max_time = 2
    source_type = [
        Device.HELTEC_V3,
        Device.HELTEC_T114,
    ]
    dst_type = Device.SEEED_WIO_TRACKER_L1_PRO

    file_id = 1

    print("Connecting devices")
    # Connect to your device
    #    dut_mesh = await MeshCore.create_ble(bluetooth, pin=bluetooth_pin)
    send_mesh = await MeshCore.create_serial(path_0)
    recv_mesh = await MeshCore.create_serial(path_1)
    dut_mesh = await MeshCore.create_serial(path_2)

    source = [
        send_mesh,
        recv_mesh,
    ]

    dut = DUT(dut_mesh)
    loss_test = Loss(
        frames_sent=frame_count,
        granularity=granularity,
        prop_min_time=prop_min_time,
        prop_max_time=prop_max_time,
        num_rtts=n_rtts,
        max_timeout=max_time,
    )

    dut.run_test()
    file_id = await loss_test.run_test(
        source=source,
        dut_name=contact_under_test,
        src_type=source_type,
        dst_type=dst_type,
        num_frame_sizes=num_frame_sizes,
        distance=None,
        notes="testing thangs",
    )

    await dut_mesh.disconnect()
    await send_mesh.disconnect()
    await recv_mesh.disconnect()

    results = LossResults(file_name=file_id)

    results.disp_results()


if __name__ == "__main__":
    """Python main"""
    asyncio.run(main())
