import asyncio
import sys

# Import directly from the meshcore library as you specified
from meshcore import EventType, MeshCore


async def test_mesh_contacts(serial_port: str):
    print("1. Initializing MeshCore...")

    print(f"2. Configuring serial connection on {serial_port}...")
    # Initialize the serial port connection
    mesh = await MeshCore.create_serial(serial_port)

    print("3. Connecting to the mesh radio...")
    await mesh.connect()

    try:
        print("4. Waiting for contacts to synchronize (Timeout in 30s)...")
        # Await the built-in function to ensure nodes are downloaded from the radio
        await asyncio.wait_for(mesh.ensure_contacts(), timeout=30.0)

        contacts = mesh.contacts

        if not contacts:
            print("\n[!] The contacts list is completely empty.")
            print("The radio hasn't discovered other nodes on the network yet.")
            return

        print(f"\n✅ Successfully loaded {len(contacts)} contacts!")
        print("-" * 60)

        # Print every contact to reveal exact naming (including hidden spaces or case issues)
        if isinstance(contacts, dict):
            for node_id, contact_obj in contacts.items():
                name = getattr(contact_obj, 'name', 'Unknown')
                print(f"ID: {node_id:<15} | Exact Name: '{name}' | Object: {contact_obj}")
        elif isinstance(contacts, list):
            for contact_obj in contacts:
                name = getattr(contact_obj, 'name', 'Unknown')
                print(f"Exact Name: '{name}' | Object: {contact_obj}")
        else:
            # Fallback if contacts is stored in an unexpected format
            print(contacts)

        print("-" * 60)

        target = "Gateway"
        print(f"\n5. Testing get_contact_by_name('{target}')...")

        # Test the exact lookup method you are using in your web server
        found = mesh.get_contact_by_name(target)

        if found:
            print(f"✅ Success! Found the contact object: {found}")
        else:
            print(f"❌ Failed to find '{target}'.")
            print("Check the printed list above for exact spelling, capitalization, or missing devices.")

    except asyncio.TimeoutError:
        print("\n[!] Timeout Error: The radio never finished loading the contacts.")
    except Exception as e:
        print(f"\n[!] Unexpected Error: {e}")
    finally:
        print("\nDisconnecting...")
        await mesh.disconnect()


if __name__ == "__main__":
    # SET YOUR SERIAL PORT HERE
    # Linux/Mac usually: "/dev/ttyUSB0" or "/dev/cu.usbserial-0001"
    # Windows usually: "COM3" or "COM4"
    PORT = "/dev/cu.usbmodem101"

    # Run the async loop
    asyncio.run(test_mesh_contacts(PORT))

    from meshcore import EventType

    # This will print all the valid attributes inside EventType to your console
    print("Available EventTypes:", [e for e in dir(EventType) if not e.startswith("__")])