import asyncio
from meshcore import MeshCore, EventType

meshcore = MeshCore.create_serial("/dev/ttyUSB0")

async def main():
    

    result = await meshcore.commands.get_contacts()
    if result.type == EventType.ERROR:
        print(f"Error getting contacts: {result.payload}")
        return

    for contact in result:
        print(f"contact: {contact}")
    
        
    contacts = result.payload
    print(f"Found {len(contacts)} contacts")
    
    if contacts:
        # Get the first contact
        contact = next(iter(contacts.items()))[1]
        
        # Pass the contact object directly to send_msg
        result = await meshcore.commands.send_msg(contact, "Hello QCNJ")
        
        if result.type == EventType.ERROR:
            print(f"Error sending message: {result.payload}")
        else:
            print("Message sent successfully!")
    
    await meshcore.disconnect()


async def handle_message(event):
    data = event.payload
    print(f"Message from {data['pubkey_prefix']}: {data['text']}")
    
subscription = meshcore.subscribe(EventType.CONTACT_MSG_RECV, handle_message)

meshcore.unsubscribe(subscription)

asyncio.run(main())
