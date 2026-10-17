"""For recieving messages from a DUT (requires a thread)

Resources:
    https://docs.python.org/3/library/threading.html
    https://pypi.org/project/meshcore/
"""
import sys
import asyncio
import threading
from meshcore import MeshCore, EventType
from meshcore.events import Event

class Reciever:
    """For recieving messages for the Loss test"""

    reciever: MeshCore
    dut: str
    testing: bool
    n_recieved: int
    cv: threading.Condition
    thread: threading.Thread

    def __init__(
        self,
        reciever: MeshCore,
        dut: str,
    ) -> None:
        """Initialzie this reciever (for loss testing)

        Args:
            reciever (MeshCore): The device which is recieving messages
            dut (ditc): Public key prefix of DUT
	    """
        self.reciever = reciever
        self.dut = dut
        self.testing = False
        self.n_recieved = 0
        self.cv = threading.Condition()
        self.thread = threading.Thread(
            target = self.thread_entry,
        )

    def inc_counter(
        self,
        recieved_msg: Event,
    ) -> None:
        """Continue the count!

        Args:
            recieved_msg (EventType): Message recieved o7

        Resources:
            https://www.geeksforgeeks.org/python/python-sys-stdout-flush/
            https://www.geeksforgeeks.org/python/string-comparison-in-python/
        """
        if recieved_msg['pubkey_prefix'] == self.dut:
            print(f"recieved: {recieved_msg['text']}")
            sys.stdout.flush()
            self.n_recieved += 1

    async def thread_loop(self) -> None:
        """Run da thread
        """
        # Start auto-fetching messages
        await self.reciever.start_auto_message_fetching()

        self.reciever.subscribe(
            event_type = EventType.CONTACT_MSG_RECV,
            callback = self.inc_counter,
        )

        with self.cv:
            while self.testing:
                # Wait here until the test is done
                self.cv.wait()

        await self.reciever.stop_auto_message_fetching()

    def thread_entry(self) -> None:
        """Threads expect non-async functions, send 'em here
        """
        asyncio.run(self.thread_loop())

    def start(self) -> None:
        """Star the test!
        """
        self.n_recieved = 0
        self.testing = True
        self.thread.start()

    def stop(self) -> int: #TODO: causing error
        """Stop the count

        Returns:
             count (int): Number of messages recieved since start() call
        """
        with self.cv:
            self.testing = False
            self.cv.notify()
        self.thread.join()
        return self.n_recieved

async def main():
    """For testing purposes

    Resources:
        https://www.geeksforgeeks.org/python/sleep-in-python/
    """
    from time import sleep
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
                reciever = Reciever(
                    reciever = meshcore,
                    dut = contact['public_key'],
                )

                reciever.start()
                await asyncio.sleep(20)
                print("Test ends in 10s")
                await asyncio.sleep(10)
                print(f"messages recieved: {reciever.stop()}")

    await meshcore.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
