import asyncio
import argparse

from meshcore import MeshCore, EventType


"""
python -m cyberStuff.send_raw \
--port /dev/ttyACM0 \
--hex "31d50a006dcfa4a3a7141b9cc46ada66ba161d8a659f72c4"   #this is a vailid one captured sent to test_user
"""
import inspect
from meshcore import MeshCore



async def main():
    # mesh = await MeshCore.create_serial("/dev/ttyACM0", debug=True)
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",default="/dev/ttyACM1",help="USB serial port"
    )
    parser.add_argument(
        "--hex",
        required=True,
        help="Complete encoded MeshCore packet in hex"
    )

    args = parser.parse_args()

    try:
        packet = bytes.fromhex(args.hex)
    except ValueError:
        print("Invalid hexadecimal input")
        return
    
    if not packet:
        print("needs packer")
        return
    
    mesh = await MeshCore.create_serial(
        args.port,
        115200,
        debug=True
    )
    print("here")

    try:
        print(f"connected to to {args.port}")
        print(f"sending: {packet.hex()}")
        print(f"length: {len(packet)} bytes")

        result = await mesh.commands.send_raw_packet(
        packet,
        priority=0
        )

        if result.type == EventType.ERROR:
            print(f"failed: {result.payload}")
        else:
            print("sent!")


    finally:
        await mesh.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

