"""A Metadata object for consistency + modularity

Resources:
    https://docs.python.org/3/tutorial/classes.html
    https://www.geeksforgeeks.org/python/method-and-constructor-overloading-in-python/
"""

import json
from pathlib import Path
from warnings import warn

import matplotlib.pyplot as plt
import numpy as np

from ..Results import Results
from ..util.Device import Device


class LatencyResults(Results):
    """The metadata to track"""

    _all_results: bool
    _src_type: Device
    _dst_type: Device
    _distance: float | None  # TODO: make this not optional
    _num_frame_sizes: int
    _max_msgs: int
    _max_time: int
    _notes: str | None
    _frame_sizes: np.ndarray
    _latencies: np.ndarray
    _TEST_RESULTS_PATH: Path = Path("latency_test_results/")

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
        self._all_results = False
        if file_name:
            self.load_results(file_name)
        elif (
            src_type is None
            or dst_type is None
            or num_frame_sizes is None
            or max_msgs is None
            or max_time is None
            or frame_sizes is None
            or latencies is None
        ):
            if not (
                src_type is None
                and dst_type is None
                and num_frame_sizes is None
                and max_msgs is None
                and max_time is None
                and frame_sizes is None
                and latencies is None
            ):
                warn("Not all necessaray data given, defaulting to existing results")
            self._all_results = True
        else:
            self._src_type = src_type
            self._dst_type = dst_type
            self._distance = distance
            self._num_frame_sizes = num_frame_sizes
            self._max_msgs = max_msgs
            self._max_time = max_time
            self._notes = notes
            self._frame_sizes = frame_sizes
            self._latencies = latencies

    def __plot_latency_v_iter(self) -> None:
        """Display the latencies"""
        xs = range(self._latencies.shape[1])

        for i, frame_size in enumerate(self._frame_sizes):
            plt.plot(xs, self._latencies[i], label=f"{frame_size}")

        plt.ylabel("Latency (s)")
        plt.xlabel("Itteration")
        plt.legend()
        plt.show()
        plt.close()

    def __hold_off(self) -> None:
        """Display the loaded results!"""
        plt.title("MeshCore Latency")
        plt.legend()
        plt.ylabel("Latency (s)")
        plt.xlabel("Frame Size (bytes)")
        plt.show()
        plt.close()

    def __plot_latency_v_fsize(self, hold_on: bool = False) -> None:
        """Display the latencies as requested in the RFC

        Resources:
            https://numpy.org/doc/2.1/reference/generated/numpy.nanmean.html
        """
        frame_lats = np.nanmean(
            self._latencies, axis=1
        )  # Average latency per frame size

        if hold_on and self._distance is not None and self._distance < 100000:
            plt.plot(
                self._frame_sizes, frame_lats, label=f"{round(self._distance)} meters"
            )
        else:
            if hold_on:
                hold_on = False
                warn("Switching to hold on, due to something not being set properly")
            plt.plot(self._frame_sizes, frame_lats)

        if not hold_on:
            plt.ylabel("Latency (s)")
            plt.xlabel("Frame Size (bytes)")
            plt.show()
            plt.close()

    def load_results(self, file_name: int) -> None:
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
            self._src_type = Device(metadata["src_type"])
            self._dst_type = Device(metadata["dst_type"])
            self._distance = metadata["distance"]
            self._num_frame_sizes = metadata["num_frame_sizes"]
            self._max_msgs = metadata["max_msgs"]
            self._max_time = metadata["max_time"]
            self._notes = metadata["notes"]

        npzfile = np.load(path_npz)
        self._frame_sizes = npzfile["frame_sizes"]
        self._latencies = npzfile["latencies"]

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
            "src_type": self._src_type.name,
            "dst_type": self._dst_type.name,
            "distance": self._distance,
            "num_frame_sizes": self._num_frame_sizes,
            "max_msgs": self._max_msgs,
            "max_time": self._max_time,
            "notes": self._notes,
        }
        with open(path_json, "w") as json_file:
            json.dump(metadata, json_file, indent=4)

        np.savez(path_npz, frame_sizes=self._frame_sizes, latencies=self._latencies)

        return save_file

    def disp_results(self) -> None:
        """Display test results"""
        if self._all_results:
            for i in range(self.next_available_filename()):
                try:
                    self.load_results(i)
                    if self._distance is not None:
                        self.__plot_latency_v_fsize(hold_on=True)
                except FileNotFoundError:
                    pass

            self.__hold_off()
        else:
            self.__plot_latency_v_iter()
            self.__plot_latency_v_fsize()


def main() -> None:
    """display results from a loss test"""
    # file_ids = range(1, 4)

    # for file_id in file_ids:
    #    results = LatencyResults(file_name=file_id)
    #    results.disp_results()
    results = LatencyResults()
    results.disp_results()


if __name__ == "__main__":
    """Python main"""
    main()
