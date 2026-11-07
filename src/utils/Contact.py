import os
import asyncio
import json

from dotenv import load_dotenv

from meshcore import EventType, MeshCore
from meshcore.events import Event



async def main() -> None:
    load_dotenv()
    path = os.getenv("MESH_PATH")
    device = await MeshCore.create_serial(path)
    meshcore_contacts: dict[str, str]
    with open("secrets.json") as json_file:
            data = json.load(json_file)
            meshcore_contacts = data["MESHCORE_CONTACT_INFO"]  
    for public_key, adv_name in meshcore_contacts.items():
        contact_data = {
            "public_key": public_key,
            "adv_name": adv_name,
            "type": 1,
            "flags":0
        }
        
    
        await device.commands.add_contact(contact_data)
        print(f"Added {adv_name}")


if __name__ == "__main__":
    asyncio.run(main())
 