"""The frame loss test"""
import warnings
import asyncio
import numpy as np
from meshcore import MeshCore

from ...results.LossResults import LossResults
from ...util.Device import Device
from ..Test import Test
from .Sender import Sender
from .Receiver import Receiver

TIMEOUT_BTWN_FRAME_SIZES = 5 #Timeout for five seconds between messages

class Loss(Test):
    """The latency test class"""

    frames_sent: int
    granularity: float

    def __init__(
        self,
        frames_sent: int,
        granularity: float,
        prop_min_time: float | None = None,
        prop_max_time: float | None = None,
    ) -> None:
        """Initialize this Loss Test object

        Args:
            frames_sent (int): Number of frames for this test
            granularity (float): Proportion to decrease frame rate per test
        """
        self.frames_sent = frames_sent
        self.granularity = granularity
        if prop_min_time:
            assert prop_min_time < 1, f"{prop_min_time} >= 1"
            self.prop_min_time = prop_min_time
        if prop_max_time:
            assert prop_max_time > 1, f"{prop_max_time} <= 1"
            self.prop_max_time = prop_max_time

    def get_timeouts(
        self,
        min_times: np.ndarray,
    ) -> np.ndarray:
        """Get the timeout times

        Args:
            min_times (np.ndarray): The initial timeout times of the tests
            num_frame_sizes (int): The number of frame sizes

        Returns:
             timeouts (np.ndarray): The timeout times for every frame size
	    """
        num_frame_sizes = min_times.shape[0]
        init_timeouts = min_times * self.prop_min_time
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

        return 1 / fpss

    async def run_test(
        self,
        source: MeshCore | list[MeshCore],
        dut_name: str,
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
            dut (str): The contact name of the device under test (must be same
            for all devices)
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
        assert type(source) is list, f"need more than one source device: {type(source)}"
        assert type(src_type) is list, f"need more than one source device: {type(src_type)}"
        assert distance is None or type(distance) is list, f"need more than one source device: {type(distance)}"
        assert len(source) == len(src_type), f"{len(source)} != {len(src_type)}"
        assert distance is None or len(source) == len(distance), f"{len(source)} != {len(src_type)}"
        if (len(source) % 2 != 0):
            warnings.warn(f"Odd number of source devices: {len(source)}")

        dut_contacts = []
        for source_dev in source:
            print(f"source_dev: {source_dev}")
            if source_dev is None:
                raise ValueError(f"None source: {source}")
            # Get your contacts
            result = await source_dev.commands.get_contacts()
            contacts = result.payload
            if contacts:
                for contact in contacts.values():
#                    print(f"contact: {contact}")
                    if contact["adv_name"] == dut_name:
                        dut_contacts.append(contact)
                        break
        assert len(source) == len(dut_contacts), f"Source device does not have DUT in contacts: {dut_contacts}"

        num_src = len(source) // 2
        send_devs = source[:num_src]
        recv_devs = source[num_src:]
        senders: list[Sender] = []
        receivers: list[Receiver] = []
        needs_thread = False
        frames_per_dev = self.frames_sent // num_src
        actual_frames_sent = frames_per_dev * num_src

        if len(send_devs) > 1:
            # More than one sending device -> give 'em all a thread
            needs_thread = True

        for i in range(num_src):
            new_sender = Sender(
                sender = send_devs[i],
                dut = dut_contacts[i],
                frames_to_send = frames_per_dev,
                needs_thread = needs_thread,
            )
            new_receiver = Receiver(
                reciever=recv_devs[i],
                dut_pub_key=dut_contacts[i]['public_key'],
            )
            senders.append(new_sender)
            receivers.append(new_receiver)

        # TODO: handshake (ensure DUT has map of sending devices to recieving devs)

        frame_sizes = self.get_frame_sizes(num_frame_sizes=num_frame_sizes)
        min_times, max_times = await self.rtt_time(
            source=send_devs,
            dut=dut_contacts,
            frame_sizes=frame_sizes,
        )

        timeouts = self.get_timeouts(min_times)
        frames_received = np.full(timeouts.shape, np.nan)

        #TODO: do test for various frame sizes, setting timeouts along the way
        for i, frame_size in enumerate(frame_sizes):
            print(f"Loss Test: frame_size of {frame_size}")
            no_loss_prev = False
            for j, timeout_time in enumerate(timeouts[i]):
                # Start recievers first to track all messages
                for receiver in receivers:
                    await receiver.start()

                # Start sending messages
                for sender in senders:
                    await sender.start(
                        msg_size = frame_size,
                        timeout = timeout_time,
                    )

                # Wait for sending to finish
                for sender in senders:
                    sender.stop()

                # Sleep a bit to ensure everything has time to finish
                await asyncio.sleep(max_times[i] * self.prop_max_time)

                # Stop the count!
                for reciever in receivers:
                    frames_received[i, j] += await reciever.stop()

                no_loss_curr = frames_received[i, j] == actual_frames_sent
                if no_loss_prev and no_loss_curr:
                    break
                no_loss_prev = no_loss_curr

        results = LossResults(
            src_type=src_type,
            dst_type=dst_type,
            distance=distance,
            num_frame_sizes=num_frame_sizes,
            frames_sent=actual_frames_sent,
            granularity=self.granularity,
            num_send_nodes=len(send_devs),
            num_recv_nodes=len(recv_devs),
            notes=notes,
            frame_sizes=frame_sizes,
            min_timeouts=min_times * self.prop_min_time,
            frames_recvd=frames_received,
            timeout_times=timeouts,
        )
        file_id = results.save_results()

        return file_id


# TODO: TEST THIS BADDIE
async def main():
    """For testing purposes
    """
    contact_under_test = "T114_0"
    frame_count = 5
    granularity = 0.1 # 10% is maximum granularity
    num_frame_sizes = 5 # 5 is minimum
    prop_min_time = 0.9
    prop_max_time = 2
    source_type = [
        Device.HELTEC_V3,
        Device.HELTEC_V3,
    ]
    dst_type = Device.HELTEC_T114


    file_id = 1

    # Connect to your device
    send_mesh = await MeshCore.create_serial("/dev/ttyUSB0")
    recv_mesh = await MeshCore.create_serial("/dev/ttyUSB1")

    source = [
        send_mesh,
        recv_mesh,
    ]

    # Get your contacts
    result = await recv_mesh.commands.get_contacts()
    contacts = result.payload

    # Send a message to T114-j
    if contacts:
        for contact in contacts.values():
            if contact["adv_name"] == contact_under_test:
                loss_test = Loss(
                        frames_sent=frame_count,
                        granularity=granularity,
                        prop_min_time=prop_min_time,
                        prop_max_time=prop_max_time,
                )
                file_id = await loss_test.run_test(
                    source=source,
                    dut_name=contact_under_test,
                    src_type=source_type,
                    dst_type=dst_type,
                    num_frame_sizes=num_frame_sizes,
                    distance=None,
                    notes="testing thangs",
                )

    results = LossResults(file_name=file_id)
    results.disp_results()

    await send_mesh.disconnect()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
