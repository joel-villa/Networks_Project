"""Runnable main"""

import os
import asyncio

from dotenv import load_dotenv
from gateway import Gateway

from meshcore import EventType, MeshCore
from meshcore.events import Event



async def main() -> None:
    load_dotenv()
    path = os.getenv("MESH_PATH")
    device = await MeshCore.create_serial(path)
    gateway = Gateway(device)
    await gateway.run()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

