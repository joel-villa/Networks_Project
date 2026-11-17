
import os

from dotenv import load_dotenv
from meshcore.meshcore import MeshCore

from src.loss.DUT import DUT


async def main_loss() -> None:
    # Connect to your device
    load_dotenv()
    path_0 = os.getenv("MESH_PATH")
    dut_mesh = await MeshCore.create_serial(path_0)

    dut = DUT(dut_mesh)

    await dut.run_handshake(n_pairs=1)
    await dut.run_test()
    await dut.finish()

    await dut_mesh.disconnect()
