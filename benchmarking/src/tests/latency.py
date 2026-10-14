"""A file for all that latency goodness, goal take the average of 32
ping-pongs, implementing something similar to what is prescribed in RFC 2544:
    https://www.rfc-editor.org/info/rfc2544/
"""
import asyncio
import numpy as np
from time import perf_counter
from meshcore import MeshCore, EventType
from ..util.Device import Device
from ..results.LatencyResults import LatencyResults

async def round_trip_time(
    meshcore:MeshCore,
    dst_key:dict,
    message:str
) -> float:
    """Time a message's ACK

    Args:
        meshcore (MeshCore): The sending device
        dst_key (dict): The contact of the device under test
        message (str): The message to send

    Returns:
         rtt (float): The time elapsed from message sent and ACK recieved
	"""
    start = perf_counter()
    # Send the message and get information about the sent message
    sent_result = await meshcore.commands.send_msg(dst_key, message)

    # Extract the expected acknowledgment code from the message sent event
    if sent_result.type == EventType.ERROR:
        return np.nan

    expected_ack = sent_result.payload["expected_ack"].hex()

    # Wait specifically for this acknowledgment
    result = await meshcore.wait_for_event(
        EventType.ACK,
        attribute_filters={"code": expected_ack},
        timeout=5.0
    )
    stop = perf_counter()

    if result:
        return stop - start
    else:
        # Timeout -> NaN
        return np.nan

async def latency_test(
    frame_size:int,
    meshcore:MeshCore,
    dst_key:dict,
    max_msgs:int,
    max_time:int=120,
) -> np.ndarray:
    """Do a latency test: send messages of a particular size from the MeshCore
    device to the destination device, until the max number of messages is
    reached or the max amount of time has elapsed (whichever comes first)

    NOTE: RFC prescribes an average of 20 latency times (in 2 minutes there
    will be well over 20 messages, may be best to average some equally spaced
    messages)

    Args:
        frame_size (int): The frame size (bytes)
        meshcore (MeshCore): The sending device
        dst_key (dict): The contact of the device under test
        max_msgs (int): The max number of messages to send
        max_time (int): The max number of time to run the test (in seconds)

    Returns:
         times (np.ndarray): The elapsed time of every message sent
	"""
    # Making the message of the given size
    msg = 'a'
    msg = msg * frame_size

    num_msgs = 0
    elapsed_time = 0
    start_time = perf_counter()

    rtts = np.full((max_msgs,), np.nan)

    while (num_msgs < max_msgs and elapsed_time < max_time):
#        print(f"num_msgs={num_msgs}, elapsed_time={elapsed_time}")
        rtts[num_msgs] = await round_trip_time(
            meshcore=meshcore,
            dst_key=dst_key,
            message=msg,
        )

        # Update loop conditions
        num_msgs += 1
        elapsed_time = perf_counter() - start_time

    return rtts / 2 # Latency = RTT / 2

async def get_latencies(
    meshcore:MeshCore,
    dst_key:dict,
    num_frame_sizes:int=5,
    max_msgs:int=32000,
    max_time:int=120,
) -> tuple[np.ndarray, np.ndarray]:
    """Get the average latencies for all significant frame sizes

    Args:
        meshcore (MeshCore): The meshcore device doing the timing
        dst_key (dict): The contact of the device under test
        num_frame_sizes (int): The number of frame sizes
        max_msgs (int): The max number of messages to send
        max_time (int): The max number of time to run the test (in seconds)

    Returns:
         frame_sizes (np.ndarray): An array of frame sizes tested (at least 5,
         two being max and min frame size)
         latencies (np.ndarray): An array of those latencies of significance

    Resources:
        https://numpy.org/doc/stable/reference/generated/numpy.linspace.html
	"""
    frame_sizes = np.linspace(
        start=1, # Sending message of minimum size 1
        stop=150,
        num=num_frame_sizes,
        dtype=int
    )
    latencies = np.full((num_frame_sizes, max_msgs), np.nan)

    for i, frame_size in enumerate(frame_sizes):
        print(f"Timing frame size {frame_size}")
        latencies[i] = await latency_test(
            frame_size=frame_size,
            meshcore=meshcore,
            dst_key=dst_key,
            max_msgs=max_msgs,
            max_time=max_time,
        )

    return frame_sizes, latencies

async def run_test(
    meshcore:MeshCore,
    contact:dict,
    num_frame_sizes:int,
    max_msgs:int,
    max_time:int,
    src_type:Device,
    dst_type:Device,
    distance:float | None,
    notes:str | None,
) -> int:
    """Run this latency test with given specifications

    Args:
        meshcore (MeshCore): The timing device
        contact (dict): The contact which has the DUT
        num_frame_sizes (int): The number of frame sizes tested
        max_msgs (int): The maximum number of messages sent during
        test of a given frame size
        max_time (int): The maxium time of test (seconds) for a given
        frame size
        src_type (Device): The type of the timing device
        dst_type (Device): The type of the Device Under Test
        distance (float | None): The distance between the src and dst
        notes (str | None): Anything to note?

    Returns:
         file_num (int): file number the test is saved under
	"""
    print("Starting test")
    frame_sizes, latencies = await get_latencies(
        meshcore=meshcore,
        dst_key=contact,
        num_frame_sizes=num_frame_sizes,
        max_msgs=max_msgs,
        max_time=max_time,
    )
    results = LatencyResults(
        src_type=src_type,
        dst_type=dst_type,
        distance=distance,
        num_frame_sizes=num_frame_sizes,
        max_msgs=max_msgs,
        max_time=max_time,
        notes=notes,
        frame_sizes=frame_sizes,
        latencies=latencies,
    )
    file_name = results.save_results()

    return file_name

async def wrap_run_test(
    contact_under_test:str,
    num_frame_sizes:int,
    max_msgs:int,
    max_time:int,
    src_type:Device,
    dst_type:Device,
    distance:float | None,
    notes:str | None,
) -> int:
    """Wrapper for run_test()

    Args:
        contact_under_test (str): the string of the contact to test
        num_frame_sizes (int): The number of frame sizes tested
        max_msgs (int): The maximum number of messages sent during
        test of a given frame size
        max_time (int): The maxium time of test (seconds) for a given
        frame size
        src_type (Device): The type of the timing device
        dst_type (Device): The type of the Device Under Test
        distance (float | None): The distance between the src and dst
        notes (str | None): Anything to note?

    Returns:
         file_num (int): file number the test is saved under
	"""
    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")

    # Get your contacts
    result = await meshcore.commands.get_contacts()
    contacts = result.payload

    file_name = -1

    # Send a message to T114-j
    if contacts:
        for contact in contacts.values():
            if contact["adv_name"] == contact_under_test:
                file_name = await run_test(
                    meshcore=meshcore,
                    contact=contact,
                    num_frame_sizes=num_frame_sizes,
                    max_msgs=max_msgs,
                    max_time=max_time,
                    src_type=src_type,
                    dst_type=dst_type,
                    distance=distance,
                    notes=notes,
                )

    await meshcore.disconnect()

    return file_name

def view_results(file_name:int) -> None:
    """Display the results associated with the given filename

    Args:
        file_name (int): file_name
	"""
    results = LatencyResults(file_name=file_name)
    print("Displaying results")
    print(f"frame_sizes={results.frame_sizes}")
    print(f"latencies={results.latencies[:, :32]}")
    results.plot_latency_v_itter()
    results.plot_latency_v_fsize()

async def main():
    """Main for testing purposes
	"""
    contact_under_test = "T114_0"

    # TODO: get this test to under 5 minutes for scaling to larger tests
    num_frame_sizes=8 # 5 at minimum
    max_msgs=1024
    max_time=260
    src_type=Device.HELTEC_V3
    dst_type=Device.HELTEC_T114
    distance=None
    notes=None

    file_name=2

#    file_name = await wrap_run_test(
#        contact_under_test=contact_under_test,
#        num_frame_sizes=num_frame_sizes,
#        max_msgs=max_msgs,
#        max_time=max_time,
#        src_type=src_type,
#        dst_type=dst_type,
#        distance=distance,
#        notes=notes,
#    )

    view_results(file_name)

if __name__ == '__main__':
    """Main for testing purposes
    """
    asyncio.run(main())
