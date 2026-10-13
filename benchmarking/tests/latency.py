"""A file for all that latency goodness, goal take the average of 32
ping-pongs, implementing something similar to what is prescribed in RFC 2544:
    https://www.rfc-editor.org/info/rfc2544/
"""
import asyncio
import json
import numpy as np
from time import perf_counter
from meshcore import MeshCore, EventType
from enum import Enum
from pathlib import Path

TEST_RESULTS_PATH = Path("../test_results/")

class Device(Enum):
    HELTEC_V3 = 1
    HELTEC_T114 = 2
    SEEED_WIO_TRACKER_L1_PRO = 3

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
        latencies[i] = await latency_test(
            frame_size=frame_size,
            meshcore=meshcore,
            dst_key=dst_key,
            max_msgs=max_msgs,
            max_time=max_time,
        )

    return frame_sizes, latencies

def get_paths(file_name:int) -> tuple[Path,Path]:
    """Get the paths to the file name in test_results directory

    Args:
        file_name (int): The name of the file of significance

    Returns:
         path_json (Path): The path to the json file
         path_npz (Path): The path to the npz file
	"""
    path_json = TEST_RESULTS_PATH / f"{file_name}.json"
    path_npz = TEST_RESULTS_PATH / f"{file_name}.npz"
    return path_json, path_npz

def save_results(
    src_type:Device,
    dst_type:Device,
    distance:float | None,
    notes:str | None,
    frame_sizes:np.ndarray,
    latencies:np.ndarray,
) -> int:
    """Save results to npz file and metadata to a json file

    Args:
        send_typ (Device): The type of the device doing the timing

    Returns:
         save_file (int): The file name where the data was saved

    Resources:
         https://www.geeksforgeeks.org/python/python-list-files-in-a-directory/
         https://www.geeksforgeeks.org/python/convert-string-to-integer-in-python/
         https://www.w3schools.com/PYTHON/python_try_except.asp
         https://numpy.org/doc/stable/reference/generated/numpy.savez.html
         https://www.geeksforgeeks.org/python/how-to-convert-python-dictionary-to-json/
	"""
    import os

    max_file = 0

    for (root, dirs, files) in os.walk(TEST_RESULTS_PATH):
        for file in files:
            if file.endswith(".json"):
                try:
                    print(file[:-5])
                    curr_file = int(file[:-5])
                    max_file = max(max_file, curr_file)
                except:
                    pass

    save_file = max_file + 1

    metadata = {
        "src_type" : src_type.name,
        "dst_type" : dst_type.name,
        "distance" : distance,
        "notes" : notes,
    }

    path_json, path_npz = get_paths(save_file)

    np.savez(path_npz, frame_sizes=frame_sizes, latencies=latencies)
    with open(path_json, "w") as json_file:
        json.dump(metadata, json_file, indent=4)

    return save_file

def load_results(file_name:int) -> tuple[dict, np.ndarray, np.ndarray]:
    """Load the results from the provided file name

    Args:
        file_name (int): The file of significance

    Returns:
         metadata (dict): The metadata pertaining to this run
         frame_sizes (np.ndarray): The frame sizes involved in this test
         latencies (np.ndarray): The measured latencies for this test

    Resources:
        https://www.geeksforgeeks.org/python/convert-json-to-dictionary-in-python/
	"""
    metadata = {}
    path_json, path_npz = get_paths(file_name)

    with open(path_json) as json_file:
        metadata = json.load(json_file)

    npzfile = np.load(path_npz)
    frame_sizes = npzfile["frame_sizes"]
    latencies = npzfile["latencies"]

    return metadata, frame_sizes, latencies

def disp_results(
    frame_sizes:np.ndarray,
    latencies:np.ndarray,
) -> None:
    """Display the latencies

    Args:
        frame_sizes (np.ndarray): How many chars sent per test
        latencies (np.ndarray): The timings per test
	"""
    import matplotlib.pyplot as plt
    xs = range(latencies.shape[1])

    for i, frame_size in enumerate(frame_sizes):
        plt.plot(xs, latencies[i], label=f"{frame_size}")

    plt.ylabel("Latency (s)")
    plt.xlabel("Itteration")
    plt.legend()
    plt.show()
    plt.close()

def disp_requested_results(
    frame_sizes:np.ndarray,
    latencies:np.ndarray
) -> None:
    """Display the latencies as requested in the RFC

    Args:
        frame_sizes (np.ndarray): How many chars sent per test
        latencies (np.ndarray):

    Resources:
        https://numpy.org/doc/2.1/reference/generated/numpy.nanmean.html
	"""
    import matplotlib.pyplot as plt
    frame_lats = np.nanmean(latencies, axis=1) # Average latency per frame size

    plt.plot(frame_sizes, frame_lats)

    plt.ylabel("Latency (s)")
    plt.xlabel("Frame Size (bytes)")
    plt.show()
    plt.close()

async def main():
    """Main for testing purposes
	"""

    # Connect to your device
    meshcore = await MeshCore.create_serial("/dev/ttyUSB0")

    # Get your contacts
    result = await meshcore.commands.get_contacts()
    contacts = result.payload

    # Send a message to T114-j
    if contacts:
        for contact in contacts.values():
            if contact["adv_name"] == "T114-j":
                print("Starting test")
                frame_sizes, latencies = await get_latencies(
                    meshcore=meshcore,
                    dst_key=contact,
                    num_frame_sizes=8,
                    max_msgs=1024,
                    max_time=260,
                )
                file_name = save_results(
                    src_type=Device.HELTEC_V3,
                    dst_type=Device.HELTEC_T114,
                    distance=None,
                    notes=None,
                    frame_sizes=frame_sizes,
                    latencies=latencies,
                )
                _, frame_sizes, latencies = load_results(file_name)
                print("Displaying results")
                print(f"frame_sizes={frame_sizes}")
                print(f"latencies={latencies[:, :32]}")
                disp_results(frame_sizes, latencies)
                disp_requested_results(frame_sizes, latencies)

    await meshcore.disconnect()

if __name__ == '__main__':
    """Main for testing purposes
    """
    asyncio.run(main())
