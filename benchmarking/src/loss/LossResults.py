"""For storing the results of a frame loss rate test

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


class LossResults(Results):
    """The metadata to track"""

    _all_results: bool
    _src_type: list[Device]
    _dst_type: Device
    _distance: list[float] | None  # TODO: make this not optional
    _num_frame_sizes: int
    _frames_sent: int
    _granularity: float  # TODO put this everywher
    _num_send_nodes: int
    _num_recv_nodes: int
    # TODO add these guys
    _num_rtts: int  # How many rtts to do when rtt_time() is called # TODO: THESE THREE PUT EM ALL OVER
    _prop_min_time: (
        float  # What proportion of the minimum rtt is considered small enough
    )
    _prop_max_time: (
        float  # What proportion of the maximum rtt is considered small enough
    )
    _notes: str | None
    _frame_sizes: np.ndarray
    _min_timeouts: np.ndarray  # one per frame size (what is minimum possible
    # rate of message sending per frame size)
    _frames_recvd: np.ndarray  # a 2d array of ints with a row per frame size
    _timeout_times: np.ndarray  # has same dimensions as frames_recvd (this is
    # the inverse of the frame rate)

    _TEST_RESULTS_PATH: Path = Path("frame_loss_test_results/")

    def __init__(
        self,
        file_name: int | None = None,
        src_type: list[Device] | None = None,
        dst_type: Device | None = None,
        distance: list[float] | None = None,
        num_frame_sizes: int | None = None,
        frames_sent: int | None = None,
        granularity: float | None = None,
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
            src_type (list[Device] | None): The type of the timing device
            dst_type (Device | None): The type of the Device Under Test
            distance (list[float] | None): The distance between the src and dst
            num_frame_sizes (int | None): The number of frame sizes tested
            granularity (float | None): The amount to decrement the fps
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
        self._all_results = False

        if file_name:
            self.load_results(file_name)
        elif (
            src_type is None
            or dst_type is None
            or num_frame_sizes is None
            or frames_sent is None
            or granularity is None
            or num_send_nodes is None
            or num_recv_nodes is None
            or frame_sizes is None
            or min_timeouts is None
            or frames_recvd is None
            or timeout_times is None
        ):
            if not (
                src_type is None
                and dst_type is None
                and num_frame_sizes is None
                and frames_sent is None
                and granularity is None
                and num_send_nodes is None
                and num_recv_nodes is None
                and frame_sizes is None
                and min_timeouts is None
                and frames_recvd is None
                and timeout_times is None
            ):
                warn("Not all necessaray data given, defaulting to existing results")
            self._all_results = True
        else:
            self._src_type = src_type
            self._dst_type = dst_type
            self._distance = distance
            self._num_frame_sizes = num_frame_sizes
            self._frames_sent = frames_sent
            self._granularity = granularity
            self._num_send_nodes = num_send_nodes
            self._num_recv_nodes = num_recv_nodes
            self._notes = notes
            self._frame_sizes = frame_sizes
            self._min_timeouts = min_timeouts
            self._frames_recvd = frames_recvd
            self._timeout_times = timeout_times

    #        if (
    #            self._timeout_times.shape[0] != self._num_frame_sizes
    #            or self._timeout_times.shape[1] != self._frames_sent
    #        ):
    #            warn("Metadata and measured data do not coincide")

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
            src_types = metadata["src_type"]
            self._src_type = []
            for dev_type in src_types:
                self._src_type.append(Device(dev_type))
            self._dst_type = Device(metadata["dst_type"])
            self._distance = metadata["distance"]
            self._num_frame_sizes = metadata["num_frame_sizes"]
            self._frames_sent = metadata["frames_sent"]
            self._granularity = metadata["granularity"]
            self._num_send_nodes = metadata["num_send_nodes"]
            self._num_recv_nodes = metadata["num_recv_nodes"]
            self._notes = metadata["notes"]

        npzfile = np.load(path_npz)
        self._frame_sizes = npzfile["frame_sizes"]
        self._min_timeouts = npzfile["min_timeouts"]
        self._frames_recvd = npzfile["frames_recvd"]
        self._timeout_times = npzfile["timeout_times"]

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
            "src_type": self._src_type,
            "dst_type": self._dst_type,
            "distance": self._distance,
            "num_frame_sizes": self._num_frame_sizes,
            "frames_sent": self._frames_sent,
            "granularity": self._granularity,
            "num_send_nodes": self._num_send_nodes,
            "num_recv_nodes": self._num_recv_nodes,
            "notes": self._notes,
        }
        with open(path_json, "w") as json_file:
            json.dump(metadata, json_file, indent=4)

        np.savez(
            path_npz,
            frame_sizes=self._frame_sizes,
            min_timeouts=self._min_timeouts,
            frames_recvd=self._frames_recvd,
            timeout_times=self._timeout_times,
        )

        return save_file

    def __hold_off(self, is_rfc_based: bool = True) -> None:
        """Display the loaded results!

        Args:
            is_rfc_based (bool): not rfc_based -> x axis is percentage,
            is_rfc_based -> x-axis is percentage
        """
        plt.title("MeshCore Loss")
        plt.ylabel("Frame Loss (%)")
        if is_rfc_based:
            plt.xlabel("Frame Rate (%)")
        else:
            plt.xlabel("Timeout Time (seconds)")

        plt.legend()
        plt.show()
        plt.close()

    def __disp_results_verbose(
        self, is_rfc_based: bool = True, hold_on: bool = False
    ) -> None:
        """Display the test results

        Args:
            is_rfc_based (bool): True -> x axis is percentage, false -> x axis
            is time
        """
        xs = 1 / self._timeout_times

        for i in range(xs.shape[0]):
            max_frame_rate = np.max(xs[i])
            xs[i] = (xs[i] / max_frame_rate) * 100

            if not np.isclose(np.max(xs[i]), 100):
                warn("Expected max frame rate to be 100%")

        ys = ((self._frames_sent - self._frames_recvd) / self._frames_sent) * 100

        if hold_on and self._distance is not None and min(self._distance) < 100000:
            dist = round(min(self._distance))
            for i, frame_size in enumerate(self._frame_sizes):
                if frame_size != 150:
                    warn(
                        f"skipping frame size {frame_size}, since hold on is True, only displaying frame sizes of 150"
                    )
                    continue
                if is_rfc_based:
                    plt.plot(xs[i], ys[i], label=f"{dist} meters")
                else:
                    plt.plot(self._timeout_times[i], ys[i], label=f"{dist} meters")
        else:
            if hold_on:
                hold_on = False
                warn("Switching to hold on, due to something not being set properly")

            for i, frame_size in enumerate(self._frame_sizes):
                if is_rfc_based:
                    plt.plot(xs[i], ys[i], label=f"{frame_size}")
                else:
                    plt.plot(self._timeout_times[i], ys[i], label=f"{frame_size}")

        if not hold_on:
            self.__hold_off()

    def disp_results(self) -> None:
        if self._all_results:
            for i in range(self.next_available_filename()):
                try:
                    self.load_results(i)
                    if self._distance is not None:
                        self.__disp_results_verbose(hold_on=True)
                except FileNotFoundError:
                    pass

            self.__hold_off()

        else:
            self.__disp_results_verbose()


def main() -> None:
    """display results from a loss test"""
    results = LossResults()
    results.disp_results()


if __name__ == "__main__":
    """Python main"""
    main()
