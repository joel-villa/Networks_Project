import asyncio
import logging

from meshcore import MeshCore, EventType

logging.basicConfig(level=logging.INFO)

PORT = "/dev/ttyUSB0"
CHANNEL_IDX = 0
CHANNEL_NAME = "MeshedUp"
CHANNEL_SECRET = bytes.fromhex("aa27c63feeacd8e835d02d243a17c409")


def make_reply(text: str) -> str | None:
    """Parse te responce"""
    if text.strip().lower() == "hello":
        return "Hello to you"
    return "huh"


async def main():
    mc = await MeshCore.create_serial(PORT)

   
    result = await mc.commands.set_channel(CHANNEL_IDX, CHANNEL_NAME, CHANNEL_SECRET)
    if result.type == EventType.ERROR:
        print(f"Failed to set channel: {result.payload}")
        await mc.disconnect()
        return
    print(f"Channel {CHANNEL_IDX} configured as '{CHANNEL_NAME}'")
    
    async def handle_channel_message(event):
        payload = event.payload
        if payload.get("channel_idx") != CHANNEL_IDX:
            return

        text = payload.get("text", "")
        print(f"[chan {payload['channel_idx']}] {text}")

        reply = make_reply(text)
        if reply is None:
            return

        send_result = await mc.commands.send_chan_msg(CHANNEL_IDX, reply)
        if send_result.type == EventType.ERROR:
            print(f"Failed to send reply: {send_result.payload}")
        else:
            print(f"Sent: {reply}")

    async def handle_ack(event):
        print("Message acknowledged!")

    mc.subscribe(EventType.CHANNEL_MSG_RECV, handle_channel_message)
    mc.subscribe(EventType.ACK, handle_ack)

   
    await mc.start_auto_message_fetching()

  
    await mc.commands.send_advert(flood=True)

    print("Connected ")
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