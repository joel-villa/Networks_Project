
import asyncio
import json
from datetime import datetime

from meshcore import MeshCore, EventType

PORT = "/dev/ttyACM1"


def make_serializable(obj):
    if isinstance(obj, bytes):
        return obj.hex()

    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [make_serializable(v) for v in obj]

    return obj


def save_event(name, event):
    timestamp = datetime.now().isoformat()

    record = {
        "timestamp": timestamp,
        "event": name,
        "payload": make_serializable(event.payload)
    }

   
    print(f"event: {name}")
    print(json.dumps(record, indent=2))





async def handle_raw(event):
    print("payload:", json.dumps(
        make_serializable(event.payload),
        indent=2
    ))

    payload = event.payload

    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, bytes):
                print(f"{key}: {value.hex()}")
                print(f"{key} length: {len(value)} bytes")


async def handle_rx_log(event):
    

    payload = make_serializable(event.payload)

    print(json.dumps(payload, indent=2))

    if isinstance(event.payload, dict):
        raw = event.payload.get("raw_hex")
        if raw:
            print("Raw hex length:", len(raw) // 2)



# async def handle_rx_log(event):
#     save_event("RX_LOG_DATA", event)


async def handle_message(event):
    save_event("CONTACT_MSG_RECV", event)


async def main():
    mesh = await MeshCore.create_serial(
        PORT,
        115200,
        debug=True
    )

    mesh.subscribe(EventType.RAW_DATA, handle_raw)
    mesh.subscribe(EventType.RX_LOG_DATA, handle_rx_log)
    mesh.subscribe(EventType.CONTACT_MSG_RECV, handle_message)

    print(f"Listening on {PORT}")
    print("Send a message or raw-data packet to this device.")
    print("Press CTRL+C to stop.")

    try:
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print() #i think we need this to give it a second to fulsh

    finally:
        await mesh.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
