"""A Metadata object for consistency + modularity

Resources:
    https://docs.python.org/3/tutorial/classes.html
    https://www.geeksforgeeks.org/python/method-and-constructor-overloading-in-python/
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from ..util.Device import Device
from .Results import Results


class LatencyResults(Results):
    """The metadata to track
	"""
    src_type: Device
    dst_type: Device
    distance: float | None # TODO: make this not optional
    num_frame_sizes: int
    max_msgs: int
    max_time: int
    notes: str | None
    frame_sizes: np.ndarray
    latencies: np.ndarray
    TEST_RESULTS_PATH: Path = Path("benchmarking/latency_test_results/")

    def __init__(
        self,
        file_name: int | None = None,
        src_type: Device | None = None,
        dst_type: Device | None = None,
        distance: float | None = None,
        num_frame_sizes: int | None = None,
        max_msgs: int | None = None,
        max_time: int | None = None,
        notes: str | None = None,
        frame_sizes: np.ndarray | None = None,
        latencies: np.ndarray | None = None,
    ) -> None:
        """Initialize the Metadata object

        Args:
            src_type (Device | None): The type of the timing device
            dst_type (Device | None): The type of the Device Under Test
            distance (float | None): The distance between the src and dst
            num_frame_sizes (int | None): The number of frame sizes tested
            max_msgs (int | None): The maximum number of messages sent during
            test of a given frame size
            max_time (int | None): The maxium time of test (seconds) for a given
            frame size
            notes (str | None): Anything to note?
            frame_sizes (np.ndarray | None): The tested frame sizes
            latencies (np.ndarray | None): The measured latencies (RTT divided
            by 2)
        """
        if file_name:
            self.load_results(file_name)

        else:
            if (
                src_type is None or
                dst_type is None or
                num_frame_sizes is None or
                max_msgs is None or
                max_time is None or
                frame_sizes is None or
                latencies is None
            ):
                raise ValueError(
                    "if file_name is None, all other fields "
                    "all other fields besides notes and distance cannot be "
                    "None"
                )
            self.src_type = src_type
            self.dst_type = dst_type
            self.distance = distance
            self. num_frame_sizes = num_frame_sizes
            self.max_msgs = max_msgs
            self.max_time = max_time
            self.notes = notes
            self.frame_sizes = frame_sizes
            self.latencies = latencies

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
            self.max_msgs = metadata['max_msgs']
            self.max_time = metadata['max_time']
            self.notes = metadata['notes']

        npzfile = np.load(path_npz)
        self.frame_sizes = npzfile["frame_sizes"]
        self.latencies = npzfile["latencies"]

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
            "src_type": self.src_type.name,
            "dst_type": self.dst_type.name,
            "distance": self.distance,
            "num_frame_sizes": self.num_frame_sizes,
            "max_msgs": self.max_msgs,
            "max_time": self.max_time,
            "notes": self.notes,
        }
        with open(path_json, "w") as json_file:
            json.dump(metadata, json_file, indent=4)

        np.savez(
            path_npz,
            frame_sizes=self.frame_sizes,
            latencies=self.latencies
        )

        return save_file

    def plot_latency_v_iter(
        self
    ) -> None:
        """Display the latencies
        """
        xs = range(self.latencies.shape[1])

        for i, frame_size in enumerate(self.frame_sizes):
            plt.plot(xs, self.latencies[i], label=f"{frame_size}")

        plt.ylabel("Latency (s)")
        plt.xlabel("Itteration")
        plt.legend()
        plt.show()
        plt.close()


    def plot_latency_v_fsize(
        self
    ) -> None:
        """Display the latencies as requested in the RFC

        Resources:
            https://numpy.org/doc/2.1/reference/generated/numpy.nanmean.html
        """
        frame_lats = np.nanmean(self.latencies, axis=1) # Average latency per frame size

        plt.plot(self.frame_sizes, frame_lats)

        plt.ylabel("Latency (s)")
        plt.xlabel("Frame Size (bytes)")
        plt.show()
        plt.close()

    def disp_results(self) -> None:
        """Display test results
        """
        self.plot_latency_v_iter()
        self.plot_latency_v_fsize()
