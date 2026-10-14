"""Metadata super class

Resources:
    https://realpython.com/python-interface/
"""
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
