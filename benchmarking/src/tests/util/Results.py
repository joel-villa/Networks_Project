"""Metadata super class

Resources:
    https://realpython.com/python-interface/
"""
import os
from abc import ABC, abstractmethod
from pathlib import Path

class Metadata(ABC):
    """Interface for Metadata"""
    TEST_RESULTS_PATH: Path

    def get_paths(self, file_name: int) -> tuple[Path,Path]:
        """Get the paths to the file name in test_results directory

        Args:
            self: This LatencyMetadata instance
            file_name (int): The name of the file of significance

        Returns:
            path_json (Path): The path to the json file
            path_npz (Path): The path to the npz file
        """
        path_json = self.TEST_RESULTS_PATH / f"{file_name}.json"
        path_npz = self.TEST_RESULTS_PATH / f"{file_name}.npz"
        return path_json, path_npz

    def next_available_filename(self) -> int:
        """Get the current maximum filename under the results path

        Args:
            name (type): Description

        Returns:
             maximum (int): The maximum file number currently
        """
        curr_max = 0
        for (root, dirs, files) in os.walk(self.TEST_RESULTS_PATH):
            for file in files:
                if file.endswith(".json"):
                    try:
                        curr_file = int(file[:-5])
                        curr_max = max(curr_max, curr_file)
                    except:
                        pass
        return curr_max + 1

    @abstractmethod
    def load_results(self, file_name:int) -> None:
        """Load the results from the provided file name

        Args:
            file_name (int): The file of significance
        """

    @abstractmethod
    def save_results(self) -> int:
        """Save results to npz file and metadata to a json file

        Returns:
            save_file (int): The file name where the data was saved
        """
