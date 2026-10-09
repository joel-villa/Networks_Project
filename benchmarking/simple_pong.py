"""I think the example ping pong was overly complicated, and yet somehow not
what we needed, attempting a pingus pongus

RESOURCES:
    https://pypi.org/project/meshcore/
    https://www.geeksforgeeks.org/python/time-perf_counter-function-in-python/
"""

import asyncio
from meshcore import MeshCore, EventType
from time import perf_counter

# Send a message and wait for its specific acknowledgment
async def send_and_confirm_message(
    meshcore:MeshCore,
    dst_key:dict,
    message:str
) -> bool:
    # Send the message and get information about the sent message
    sent_result = await meshcore.commands.send_msg(dst_key, message)

    # Extract the expected acknowledgment code from the message sent event
    if sent_result.type == EventType.ERROR:
        print(f"Error sending message: {sent_result.payload}")
        return False

    expected_ack = sent_result.payload["expected_ack"].hex()
    print(f"Message sent, waiting for ack with code: {expected_ack}")

    # Wait specifically for this acknowledgment
    result = await meshcore.wait_for_event(
        EventType.ACK,
        attribute_filters={"code": expected_ack},
        timeout=10.0
    )

    if result:
        print("Message confirmed delivered!")
        return True
    else:
        print("Message delivery confirmation timed out")
        return False

async def main():
    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")

    # Get your contacts
    result = await meshcore.commands.get_contacts()
    if result.type == EventType.ERROR:
        print(f"Error getting contacts: {result.payload}")
        return

    contacts = result.payload
    print(f"Found {len(contacts)} contacts")

    # Send a message to T114-j
    if contacts:
        for key, contact in contacts.items():
            if contact["adv_name"] == "T114-j":

                start = perf_counter()
                message_sent = await send_and_confirm_message(
                    meshcore=meshcore,
                    dst_key=contact,
                    message="P",
                )
                stop = perf_counter()
                print(f"Message sent ({message_sent}) w/ ACK RTT time of: {stop - start}")

    await meshcore.disconnect()

if __name__ == '__main__':
    """You know the vibe, it's a main in python :D
    """
    asyncio.run(main())
