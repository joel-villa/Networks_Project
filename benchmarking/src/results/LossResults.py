""" For storing the results of a frame loss rate test

Resources:
    https://docs.python.org/3/tutorial/classes.html
    https://www.geeksforgeeks.org/python/method-and-constructor-overloading-in-python/
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from warnings import warn
from ..util.Device import Device
from .Results import Metadata


class LatencyResults(Metadata):
    """The metadata to track
	"""
    src_type: Device
    dst_type: Device
    distance: float | None # TODO: make this not optional
    num_frame_sizes: int
    frames_sent: int
    num_send_nodes: int
    num_recv_nodes: int
    notes: str | None
    frame_sizes: np.ndarray
    min_timeouts: np.ndarray # one per frame size (what is minimum possible
    # rate of message sending per frame size)
    frames_recvd: np.ndarray # a 2d array of ints with a row per frame size
    timeout_times: np.ndarray # has same dimensions as frames_recvd (this is
    # the inverse of the frame rate)

    TEST_RESULTS_PATH: Path = Path("benchmarking/frame_loss_test_results/")

    def __init__(
        self,
        file_name: int | None = None,
        src_type: Device | None = None,
        dst_type: Device | None = None,
        distance: float | None = None,
        num_frame_sizes: int | None = None,
        frames_sent: int | None = None,
        num_send_nodes: int | None = None,
        num_recv_nodes: int | None = None,
        notes: str | None = None,
        frame_sizes: np.ndarray | None = None,
        min_timeouts: np.ndarray | None = None,
        frames_recvd: np.ndarray | None = None,
        timeout_times: np.ndarray | None = None,
    ) -> None:
        """Initialize the Metadata object

        Args:
            file_name (int | None): Where the results live
            src_type (Device | None): The type of the timing device
            dst_type (Device | None): The type of the Device Under Test
            distance (float | None): The distance between the src and dst
            num_frame_sizes (int | None): The number of frame sizes tested
            frames_sent (int | None): The number of frames sent across all tests
            num_send_nodes (int | None): Number of nodes sending messages to DUT
            num_recv_nodes (int | None): Number of nodes recieving messages
            from DUT
            notes (str | None): Anything to note?
            frame_sizes (np.ndarray | None): The tested frame sizes
            min_timeouts (np.ndarray | None): Initial timeouts per frame size
            (this is 100% frame rate)
            frames_recvd (np.ndarray | None): The number of frames recieved per
            frame size per frame rate
            timeout_times (np.ndarray | None): Time between message sends
            (inverse of the frame rate)
        """
        if file_name:
            self.load_results(file_name)

        else:
            if (
                src_type is None or
                dst_type is None or
                num_frame_sizes is None or
                frames_sent is None or
                num_send_nodes is None or
                num_recv_nodes is None or
                frame_sizes is None or
                min_timeouts is None or
                frames_recvd is None or
                timeout_times is None
            ):
                raise ValueError(
                    "if file_name is None, most other fields cannot be None"
                )
            self.src_type = src_type
            self.dst_type = dst_type
            self.distance = distance
            self. num_frame_sizes = num_frame_sizes
            self.frames_sent = frames_sent
            self.num_send_nodes = num_send_nodes
            self.num_recv_nodes = num_recv_nodes
            self.notes = notes
            self.frame_sizes = frame_sizes
            self.min_timeouts = min_timeouts
            self.frames_recvd = frames_recvd
            self.timeout_times = timeout_times

        if (
            self.timeout_times.shape[0] != self.num_frame_sizes or
            self.timeout_times.shape[1] != self.frames_sent
        ):
            warn("Metadata and measured data do not coincide")

    def load_results(self, file_name:int) -> None:
        """Load the results from the provided file name

        Args:
            file_name (int): The file of significance

        Resources:
            https://www.geeksforgeeks.org/python/convert-json-to-dictionary-in-python/
        """
        metadata = {}
        path_json, path_npz = self.get_paths(file_name)

        with open(path_json) as json_file:
            metadata = json.load(json_file)
            self.src_type = Device(metadata['src_type'])
            self.dst_type = Device(metadata['dst_type'])
            self.distance = metadata['distance']
            self.num_frame_sizes = metadata['num_frame_sizes']
            self.frames_sent = metadata['frames_sent']
            self.num_send_nodes = metadata['num_send_nodes']
            self.num_recv_nodes = metadata['num_recv_nodes']
            self.notes = metadata['notes']

        npzfile = np.load(path_npz)
        self.frame_sizes = npzfile['frame_sizes']
        self.min_timeouts = npzfile['min_timeouts']
        self.frames_recvd = npzfile['frames_recvd']
        self.timeout_times = npzfile['timeout_times']

    def save_results(self) -> int:
        """Save results to npz file and metadata to a json file

        Returns:
            save_file (int): The file name where the data was saved

        Resources:
            https://www.geeksforgeeks.org/python/python-list-files-in-a-directory/
            https://www.geeksforgeeks.org/python/convert-string-to-integer-in-python/
            https://www.w3schools.com/PYTHON/python_try_except.asp
            https://numpy.org/doc/stable/reference/generated/numpy.savez.html
            https://www.geeksforgeeks.org/python/how-to-convert-python-dictionary-to-json/
        """
        save_file = self.next_available_filename()

        path_json, path_npz = self.get_paths(save_file)

        metadata = {
            'src_type': self.src_type,
            'dst_type': self.dst_type,
            'distance': self.distance,
            'num_frame_sizes': self.num_frame_sizes,
            'frames_sent': self.frames_sent,
            'num_send_nodes': self.num_send_nodes,
            'num_recv_nodes': self.num_recv_nodes,
            'notes': self.notes
        }
        with open(path_json, "w") as json_file:
            json.dump(metadata, json_file, indent=4)

        np.savez(
            path_npz,
            frame_sizes=self.frame_sizes,
            min_timeouts = self.min_timeouts,
            frames_recvd = self.frames_recvd,
            timeout_times = self.timeout_times,
        )

        return save_file

    def plot_loss_v_frame_rate(
        self
    ) -> None:
        """Display the latencies

        Resrouces:
            https://www.rfc-editor.org/info/rfc2544/#section-26.3
        """
        xs = 1 / self.timeout_times
        for i in range(xs.shape[0]):
            # Following RFC recommendations
            max_frame_rate = xs[i, xs.shape[1] - 1]
            xs[i] = 100 - (max_frame_rate - xs[i]* 100)
            if xs[i, xs.shape[1]] - 1 <=99.99999:
                warn(
                    "Expecting max to be 100% for frame size"
                    f"{self.frame_sizes[i]}, got {xs[i, xs.shape[1] - 1]}"
                )
        ys = ((self.frames_sent - self.frames_recvd) * 100) / self.frames_sent

        for i, frame_size in enumerate(self.frame_sizes):
            plt.plot(xs, ys, label=f"{frame_size}")

        plt.ylabel("Frame Loss (%)")
        plt.xlabel("Frame Rate (%)")
        plt.legend()
        plt.show()
        plt.close()
