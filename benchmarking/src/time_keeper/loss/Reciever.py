"""For recieving messages from a DUT (requires a thread)

Resources:
    https://docs.python.org/3/library/threading.html
"""
import threading
from meshcore import MeshCore

class Reciever:
    """For recieving messages for the Loss test"""

    reciever: MeshCore
    dut: dict
    testing: bool
    n_recieved: int
    thread: threading.Thread

    def __init__(
        self,
        reciever: MeshCore,
        dut: dict,
    ) -> None:
        """Initialzie this reciever (for loss testing)

        Args:
            reciever (MeshCore): The device which is recieving messages
            dut (ditc): Contact info about the dut (where to recieve from)
	    """
        pass

    def start(self) -> None:
        """Star the test!
        """
        pass

    def stop(self) -> int:
        """Stop the count

        Returns:
             count (int): Number of messages recieved since start() call
        """
        #TODO: thread.join
        pass
