"""For recieving messages from a DUT (requires a thread)

Resources:
    https://docs.python.org/3/library/threading.html
    https://pypi.org/project/meshcore/
"""

import asyncio
from difflib import ndiff
import sys
from threading import BoundedSemaphore

from meshcore import EventType, MeshCore
from meshcore.events import Event, Subscription

from ..util.constants import N_CHAR_PUB_KEY_PREFIX


class Receiver:
    """For recieving messages for the Loss test"""

    reciever: MeshCore
    subscripttion: Subscription
    dut: str
    frame_size: int
    n_recieved: int
    recvd_semaphore: BoundedSemaphore

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

        #print(f"In Receiver, dut_pub_key: {dut_pub_key}\treciever_pub_key:{reciever.self_info['public_key']}")
        self.reciever = reciever
        self.dut = dut_pub_key[:N_CHAR_PUB_KEY_PREFIX]
        self.frame_size = -1
        self.n_recieved = 0
        self.recvd_semaphore = BoundedSemaphore(value=1)

    async def __inc_counter(
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
        if received_msg.payload["pubkey_prefix"] == self.dut and self.frame_size == len(received_msg.payload['text']):
            with self.recvd_semaphore:
                self.n_recieved += 1
#                print(f"received_msg: {received_msg}")
#                print(f"in Reciever received_msg length: {len(received_msg.payload['text'])}")
#                print(f"n_recieved: {self.n_recieved}")
#                sys.stdout.flush()

        #print(f"After: {self.n_recieved}")
        #sys.stdout.flush()

    async def start(self, frame_size: int) -> None: #TODO discard stale messsages by including msg length in API
        """Star the test!

        Args:
            wait_time (float): Allows for a delayed start, to give time to
            throw-away erroneous messages
        """
        self.frame_size = frame_size
        #print("Start called")
        self.subscripttion = self.reciever.subscribe(
            event_type=EventType.CONTACT_MSG_RECV,
            callback=self.__inc_counter,
        )
        # Start auto-fetching messages
        await self.reciever.start_auto_message_fetching()

        with self.recvd_semaphore:
            self.n_recieved = 0


    async def stop(self) -> int:  # TODO: causing error
        """Stop the count

        Returns:
             count (int): Number of messages recieved since start() call
        """
        self.reciever.unsubscribe(self.subscripttion)
        await self.reciever.stop_auto_message_fetching()
        with self.recvd_semaphore:
            n_recieved = self.n_recieved
            self.n_recieved = 0
        #print(f"In Receiver.stop(), n_received = {n_recieved}")
        return n_recieved


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
                    reciever=meshcore,
                    dut_pub_key=contact["public_key"],
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
