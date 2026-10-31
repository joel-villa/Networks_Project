"""The frame loss test

Resources:
    https://docs.python.org/3/library/threading.html
"""

import asyncio
from threading import Condition

import numpy as np
from meshcore import MeshCore

from src.loss.util.Handshaker import Handshaker
from src.util.RDT import RDT

from ..Test import Test
from ..util.Device import Device
from .LossResults import LossResults
from .Receiver import Receiver
from .Sender import Sender
from .util.MsgType import MsgType

TIMEOUT_BTWN_FRAME_SIZES = 5  # Timeout for five seconds between messages


class Loss(Test):
    """The latency test class"""

    frames_sent: int
    granularity: float
    awaiting_success: bool
    cv: Condition
    handshaker: Handshaker

    def __init__(
        self,
        frames_sent: int,
        granularity: float,
        # TODO: default constructor in parent class
        prop_min_time: float | None = None,
        prop_max_time: float | None = None,
        num_rtts: int | None = None,  # How many rtts to do when rtt_time() is called
        max_timeout: float | None = None,  # The maximum timeout on lost mesage possible
    ) -> None:
        """Initialize this Loss Test object

        Args:
            frames_sent (int): Number of frames for this test
            granularity (float): Proportion to decrease frame rate per test
            prop_min_time (float | None): The proportion of the min found time
            (during warmup) that is considered minimum possible
            prop_max_time (float | None): The proportion of the min found time
            (during warmup) that is considered minimum possible
        """
        self.frames_sent = frames_sent
        self.granularity = granularity
        self.awaiting_success = True
        self.cv = Condition()
        self.handshaker = Handshaker(device_type=1)
        if prop_min_time:
            assert prop_min_time < 1, f"{prop_min_time} >= 1"
            self.prop_min_time = prop_min_time
        if prop_max_time:
            assert prop_max_time > 1, f"{prop_max_time} <= 1"
            self.prop_max_time = prop_max_time
        if num_rtts:
            assert num_rtts >= 1, f"{num_rtts} < 1"
            self.num_rtts = num_rtts
        if max_timeout:
            assert max_timeout >= 2, f"{max_timeout} < 1"
            self.max_timeout = max_timeout

    def __calculate_timeouts(
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
            1,  # max fps is 100%
            self.granularity,  # min fps is granularity
            -self.granularity,  # step size of granularity
            dtype=float,
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
        assert type(src_type) is list, (
            f"need more than one source device: {type(src_type)}"
        )
        assert distance is None or type(distance) is list, (
            f"need more than one source device: {type(distance)}"
        )
        assert len(source) == len(src_type), f"{len(source)} != {len(src_type)}"
        assert distance is None or len(source) == len(distance), (
            f"{len(source)} != {len(src_type)}"
        )

        dut_contacts = await self.get_contacts(
            local_devices=source,
            dut_name=dut_name,
        )
        assert type(dut_contacts) is list, "How do we have singular contact?"

        frame_sizes = self.get_frame_sizes(num_frame_sizes=num_frame_sizes)

        print("Measuring some rtts based on ACKs")
        min_times, max_times = await self.rtt_time(
            source=source,
            dut=dut_contacts,
            frame_sizes=frame_sizes,
        )

        # Handshake time
        handshake_result = await self.handshaker.timekeeper_handshake(
            devices=source,
            contacts=dut_contacts,
            timeout_time=max_times[-1],
        )

        send_devs, recv_devs, send_contacts, recv_contacts = handshake_result

        needs_thread = False
        if len(send_devs) > 1:
            # More than one sending device -> give 'em all a thread
            needs_thread = True

        frames_per_dev = self.frames_sent // len(send_devs)
        actual_frames_sent = frames_per_dev * len(send_devs)

        senders = []
        receivers = []
        for i, send_mesh in enumerate(send_devs):
            new_sender = Sender(
                sender=send_mesh,
                dut=send_contacts[i],
                frames_to_send=frames_per_dev,
                needs_thread=needs_thread,
            )
            senders.append(new_sender)
        for i, recv_mesh in enumerate(recv_devs):
            new_receiver = Receiver(
                reciever=recv_mesh,
                dut_pub_key=recv_contacts[i]["public_key"],
            )
            receivers.append(new_receiver)

        timeouts = self.__calculate_timeouts(min_times)
        frames_received = np.full(timeouts.shape, np.nan)

        print("Starting Test!")
        # TODO: do test for various frame sizes, setting timeouts along the way
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
                        msg_size=frame_size,
                        timeout=timeout_time,
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

        print("Test done!")
        rdt = RDT()
        for i, device in enumerate(send_devs):
            await rdt.send_msg(
                device=device,
                contact=send_contacts[i],
                message=MsgType.DONE_WITH_TEST.name,
                timeout_time=max_times[-1],
            )
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


async def main():
    """For testing purposes"""
    import os

    from dotenv import load_dotenv

    load_dotenv()
    path_0 = os.getenv("MESH_PATH")
    path_1 = os.getenv("MESH_PATH_2")
    assert path_0 is not None
    assert path_1 is not None

    contact_under_test = "T114_0"
    frame_count = 5
    granularity = 0.1  # 10% is maximum granularity
    num_frame_sizes = 2  # 5 is minimum
    prop_min_time = 0.9
    prop_max_time = 2
    n_rtts = 3
    max_time = 2
    source_type = [
        Device.HELTEC_V3,
        Device.HELTEC_V3,
    ]
    dst_type = Device.HELTEC_T114

    file_id = 1

    # Connect to your device
    send_mesh = await MeshCore.create_serial(path_0)
    recv_mesh = await MeshCore.create_serial(path_1)

    source = [
        send_mesh,
        recv_mesh,
    ]

    # Get your contacts
    result = await recv_mesh.commands.get_contacts()
    contacts = result.payload

    # Send a message to T114-j
    if contacts:  # TODO: Is this necessary anymore?
        for contact in contacts.values():
            if contact["adv_name"] == contact_under_test:
                loss_test = Loss(
                    frames_sent=frame_count,
                    granularity=granularity,
                    prop_min_time=prop_min_time,
                    prop_max_time=prop_max_time,
                    num_rtts=n_rtts,
                    max_timeout=max_time,
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
    await send_mesh.disconnect()
    await recv_mesh.disconnect()

    results = LossResults(file_name=file_id)
    results.disp_results()


if __name__ == "__main__":
    """Main for testing purposes
    """
    asyncio.run(main())
