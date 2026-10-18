"""The frame loss test"""
import warnings
import numpy as np
from meshcore import MeshCore
from ...util.Device import Device
from ..Test import Test
from .Sender import Sender
from .Receiver import Receiver

class Loss(Test):
    """The latency test class"""

    frames_sent: int
    granularity: float

    def __init__(
        self,
        frames_sent: int,
        granularity: float
    ) -> None:
        """Initialize this Loss Test object

        Args:
            max_msgs (int): The maximum messages sent during the latency
        """
        self.frames_sent = frames_sent
        self.granularity = granularity

    async def run_test(
        self,
        source: MeshCore | list[MeshCore],
        dut: dict,
        src_type: Device | list[Device],
        dst_type: Device,
        num_frame_sizes: int,
        distance: float | list[float] | None,
        notes: str | None,
    ) -> int:
        """Run the test

        Args:
            source (MeshCore | list[MeshCore]): The devices which are do the
            messaging/timing
            dut (dict): The contact info of the device under test
            srt_type (Device | list[Device]): The device types of the sources
            dst_type (Device): The device type of the dut
            num_frame_sizes (int): The number of frame sizes
            distance (float | list[float]): The distances from the sources to
            the DUT
            notes (str): Anything of note about this test?

        Returns:
             test_id (int): The id of the test
        """
        # Ensure correct input shape
        assert type(source) is list[MeshCore], "need more than one source device"
        assert type(src_type) is list[Device], "need more than one source device"
        assert type(distance) is list[float], "need more than one source device"
        assert len(source) == len(src_type), f"{len(source)} != {len(src_type)}"
        assert len(source) == len(distance), f"{len(source)} != {len(src_type)}"
        if (len(source) % 2 != 0):
            warnings.warn(f"Odd number of source devices: {len(source)}")
        for source_dev in source:
            # Get your contacts
            result = await source_dev.commands.get_contacts()
            contacts = result.payload
            if contacts and dut not in contacts.values():
                raise ValueError("Source device does not have DUT in contacts")

        num_src = len(source) // 2
        send_devs = source[:num_src]
        recv_devs = source[num_src:]
        senders: list[Sender] = []
        receivers: list[Receiver] = []
        needs_thread = False

        if len(send_devs) > 1:
            # More than one sending device -> give 'em all a thread
            needs_thread = True

        for i in range(num_src):
            new_sender = Sender(
                sender = send_devs[i],
                dut = dut,
                frames_to_send = self.frames_sent,
                needs_thread = needs_thread,
            )
            new_receiver = Receiver(
                reciever=recv_devs[i],
                dut_pub_key=dut['public_key'],
            )
            senders.append(new_sender)
            receivers.append(new_receiver)

        # TODO: handshake (ensure DUT has map of sending devices to recieving devs)

        frame_sizes = self.get_frame_sizes(num_frame_sizes=num_frame_sizes)

        min_times, _ = await self.rtt_time(
            source=send_devs,
            dut=dut,
            num_msgs=5, # Sending five messages, getting max and min
            frame_sizes=frame_sizes,
        )

        #TODO make this a function:
        init_timeouts = min_times * 0.9 # Arbitrarily decided to make min timeouts 90% fastest rtt (per frame size)
        max_fps = 1 / init_timeouts

        percentages = np.arange(
            1, # max fps is 100%
            self.granularity, # min fps is granularity
            -self.granularity, # step size of granularity
            dtype = float,
        )
        fpss = np.zeros((num_frame_sizes, percentages.shape[0]))
        for i in range(num_frame_sizes):
            fpss[i] = percentages * max_fps[i]

        timeouts = 1 / fpss

        #TODO: do test for various frame sizes, setting timeouts along the way

        return  -1
