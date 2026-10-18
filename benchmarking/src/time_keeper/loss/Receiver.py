"""For recieving messages from a DUT (requires a thread)

Resources:
    https://docs.python.org/3/library/threading.html
    https://pypi.org/project/meshcore/
"""
import sys
import asyncio
from meshcore import MeshCore, EventType
from meshcore.events import Event

class Receiver:
    """For recieving messages for the Loss test"""

    reciever: MeshCore
    dut: str
    n_recieved: int

    def __init__(
        self,
        reciever: MeshCore,
        dut_pub_key: str,
    ) -> None:
        """Initialzie this reciever (for loss testing)

        Args:
            reciever (MeshCore): The device which is recieving messages
            dut (ditc): Public key prefix of DUT
	    """
        self.reciever = reciever
        self.dut = dut_pub_key[:12]
        self.n_recieved = 0

    def inc_counter(
        self,
        received_msg: Event,
    ) -> None:
        """Continue the count!

        Args:
            recieved_msg (EventType): Message recieved o7

        Resources:
            https://www.geeksforgeeks.org/python/python-sys-stdout-flush/
            https://www.geeksforgeeks.org/python/string-comparison-in-python/
        """
        if received_msg.payload['pubkey_prefix'] == self.dut:
            self.n_recieved += 1
            # print(self.n_recieved)
            # sys.stdout.flush()

    async def start(self) -> None:
        """Star the test!
        """
        self.n_recieved = 0

        # Start auto-fetching messages
        await self.reciever.start_auto_message_fetching()

        self.reciever.subscribe(
            event_type = EventType.CONTACT_MSG_RECV,
            callback = self.inc_counter,
        )


    async def stop(self) -> int: #TODO: causing error
        """Stop the count

        Returns:
             count (int): Number of messages recieved since start() call
        """
        await self.reciever.stop_auto_message_fetching()
        return self.n_recieved

async def main():
    """For testing purposes

    Resources:
        https://www.geeksforgeeks.org/python/sleep-in-python/
    """
    contact_under_test = "T114_0"
    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")

    # Get your contacts
    result = await meshcore.commands.get_contacts()
    contacts = result.payload


    # Send a message to T114-j
    if contacts:
        for contact in contacts.values():
            if contact["adv_name"] == contact_under_test:
                print(contact)
                reciever = Receiver(
                    reciever = meshcore,
                    dut_pub_key = contact['public_key'],
                )

                await reciever.start()
                await asyncio.sleep(20)
                print("Test ends in 10s")
                await asyncio.sleep(10)
                print(f"messages recieved: {await reciever.stop()}")

    await meshcore.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
