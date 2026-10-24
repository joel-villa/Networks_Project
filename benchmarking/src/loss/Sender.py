"""For sending a message to a DUT (requires a thread)

Resources:
    https://docs.python.org/3/library/threading.html
"""

import asyncio
import threading
from time import perf_counter

from meshcore import MeshCore


class Sender:
    """For sending messages for the Loss test"""

    sender: MeshCore
    dut: dict
    frames_to_send: int
    msg_size: int
    timeout: float

    thread: threading.Thread | None  # None when only one Sender -> give it main thread?

    def __init__(
        self,
        sender: MeshCore,
        dut: dict,
        frames_to_send: int,
        needs_thread: bool,
    ) -> None:
        """Initialzie this reciever (for loss testing)

        Args:
            sender (MeshCore): The device which is sending messages
            dut (ditc): Contact info about the dut (where to recieve from)
            frames_to_send (int): The number of frames to send
            needs_thread (bool): When multiple Sender's, give them all a thread,
            else hand main thread to singular Sender
        """
        self.sender = sender
        self.dut = dut
        self.frames_to_send = frames_to_send
        self.msg_size = -1
        self.timeout = -1
        if needs_thread:
            self.thread = threading.Thread(target=self.thread_entry)
        else:
            self.thread = None

    async def thread_loop(self) -> None:
        """Send dem messages"""
        message = "a"
        message = message * self.msg_size
        while self.frames_to_send:
            start = perf_counter()
            await self.sender.commands.send_msg(self.dut, message)
            stop = perf_counter()
            await asyncio.sleep(self.timeout - (stop - start))

            self.frames_to_send -= 1

    def thread_entry(self) -> None:
        """Python threads cannot be called on async methods, thus this guy
        must exist
        """
        asyncio.run(self.thread_loop())

    async def start(
        self,
        msg_size: int,
        timeout: float,
    ) -> None:
        """Time to do some data loss tracking (sending side)

        Args:
            msg_size (int): The size of messages to send
            timeout (float): The timeout time between messages

        Resources:
            https://numpy.org/doc/stable/reference/generated/numpy.arange.html
        """
        # TODO: timeout -> incremental fps -> timeouts
        self.msg_size = msg_size
        self.timeout = timeout

        if self.thread:
            self.thread.start()
        else:
            await self.thread_loop()

    def stop(self) -> None:
        """Await the test to finish"""
        # TODO: thread.join
        if self.thread:
            self.thread.join()

        self.msg_size = -1
        self.timeout = -1


async def main():
    """For testing purposes"""
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
                sender = Sender(
                    sender=meshcore,
                    dut=contact,
                    frames_to_send=10,
                    needs_thread=False,
                )

                await sender.start(
                    msg_size=150,
                    timeout=2,
                )
                sender.stop()

    await meshcore.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
