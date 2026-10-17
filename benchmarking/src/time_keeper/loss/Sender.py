"""For sending a message to a DUT (requires a thread)"""

import threading
from meshcore import MeshCore

class Sender:
    """For sending messages for the Loss test"""

    sender: MeshCore
    dut: dict
    frames_to_send: int

    thread: threading.Thread | None # None when only one Sender -> give it main thread?

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
        pass

    def start(
        self,
        msg_size: int,
        init_timeout: float,
        granularity: float,
    ) -> None:
        #TODO: timeout -> incremental fps -> timeouts

        pass

    def stop(self) -> None:
        """ Await the test to finish
        """
        #TODO: thread.join
        pass
