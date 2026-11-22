import asyncio
import os

from dotenv import load_dotenv
from meshcore.meshcore import MeshCore

from src.loss.DUT import DUT


async def main() -> None:
    # Connect to your device
    load_dotenv()
    path_0 = os.getenv("MESH_PATH_2")
    assert path_0 is not None, ".env is not setup properly"
    dut_mesh = await MeshCore.create_serial(path_0)

    dut = DUT(dut_mesh)

    await dut.run_handshake(n_pairs=1)
    await dut.run_test()
    await dut.finish()

    await dut_mesh.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
