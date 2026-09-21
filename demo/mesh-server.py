import asyncio
import logging

from meshcore import MeshCore, EventType
from llm import get_response

# logging.basicConfig(level=logging.INFO)

PORT = "/dev/cu.usbmodem14101" # "/dev/ttyUSB0"
CHANNEL_IDX = 0
CHANNEL_NAME = "BigData" #"MeshedUp"
CHANNEL_SECRET = bytes.fromhex("4a84f3cf8a9796917cf29f1eca3e0b62") # bytes.fromhex("aa27c63feeacd8e835d02d243a17c409")

async def main():
    # Connect to the node
    mc = await MeshCore.create_serial(PORT)
   
    # Set channel
    result = await mc.commands.set_channel(CHANNEL_IDX, CHANNEL_NAME, CHANNEL_SECRET)
    if result.type == EventType.ERROR:
        print(f"Failed to set channel: {result.payload}")
        await mc.disconnect()
        return
    print(f"Channel {CHANNEL_IDX} configured as '{CHANNEL_NAME}'")
    
    # Handle incoming messages
    async def handle_channel_message(event):
        payload = event.payload

        # Ignore non-configured channel messages
        if payload.get("channel_idx") != CHANNEL_IDX:
            return

        # Extract text of incoming message
        text = payload.get("text", "")
        print(f"[chan {payload['channel_idx']}] {text}")

        # Pass incoming message to llm
        reply = await get_response(text)

        # Return llm's response
        send_result = await mc.commands.send_chan_msg(CHANNEL_IDX, reply)
        if send_result.type == EventType.ERROR:
            print(f"Failed to send reply: {send_result.payload}")
        else:
            print(f"Sent: {reply}")

    # Subscribe to channel messages
    mc.subscribe(EventType.CHANNEL_MSG_RECV, handle_channel_message)
    print("Connected to node")

    await mc.start_auto_message_fetching()
    print("Waiting for incoming messages")

    try:
        await asyncio.Event().wait()  
    except asyncio.CancelledError:
        pass
    finally:
        await mc.stop_auto_message_fetching()
        await mc.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass