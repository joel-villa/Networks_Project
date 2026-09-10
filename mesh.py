import asyncio
from meshcore import MeshCore, EventType

async def main():
    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")
    
    # Get your contacts
    result = await meshcore.commands.get_contacts()
    if result.type == EventType.ERROR:
        print(f"Error getting contacts: {result.payload}")
        return

    for contact in result:
        print(f"contact: {contact}")
    
        
    contacts = result.payload
    print(f"Found {len(contacts)} contacts")
    
    # Send a message to the first contact
    # if contacts:
    #     # Get the first contact
    #     contact = next(iter(contacts.items()))[1]
        
    #     # Pass the contact object directly to send_msg
    #     result = await meshcore.commands.send_msg(contact, "Hello from Python!")
        
    #     if result.type == EventType.ERROR:
    #         print(f"Error sending message: {result.payload}")
    #     else:
    #         print("Message sent successfully!")
    
    await meshcore.disconnect()

asyncio.run(main())
