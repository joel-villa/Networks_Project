"""Frame loss, very important, heavily influced by RFC 2544:
    https://www.rfc-editor.org/info/rfc2544/
"""

import numpy as np
from time import perf_counter
from meshcore import MeshCore, EventType


async def frame_loss_rate_test(
    num_frames:int,
    max_frame_rate:float,
    granularity:float,
    meshcore:MeshCore,
    dst_key:dict,
    frame_size:int=150,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Args:
        num_frames (int): The number of frames to send to the DUT per frame rate
        max_frame_rate (float): The initial frame rate, this is the 100%
        granularity (float): The amount to decrement the frame rate per test
        meshcore (MeshCore): The sending device
        dst_key (dict): The contact of the device under test
        frame_size (int): The frame size (bytes). NOTE: use maximum frame size,
        150 chars?

    Returns:
        frame_rates (np.ndarray): The tested frame rates
        frames_sent (np.ndarray): The total number of frames sent per frame rate
        frames_lost (np.ndarray): The total number of frames lost per frame rate
	"""
    pass
