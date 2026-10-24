"""Frame loss, very important, heavily influced by RFC 2544:
    https://www.rfc-editor.org/info/rfc2544/
"""

import numpy as np
from time import perf_counter
from meshcore import MeshCore, EventType


async def frame_loss_rate_test_send(
    num_frames: int,
    frame_size: int,
    timeout_time: float,
    meshcore: MeshCore,
    dst_key: dict,
) -> bool:
    """
    Args:
        num_frames (int): The number of frames to send to the DUT per frame rate
        frame_size (int): The frame size (bytes).
        timeout_time (float): Timeout time between message sendings
        meshcore (MeshCore): The sending device
        dst_key (dict): The contact of the device under test

    Returns:
        success (bool): Successful test?
	"""

    # NOTE: on calculating next timeout times: convert to fps then do percentages then convert back
    pass

async def frame_loss_rate_test_recv(
    meshcore: MeshCore,
    dst_key: dict,
) -> dict[int, int]:
    """
    Args:
        num_frames (int): The number of frames to send to the DUT per frame rate
        frame_size (int): The frame size (bytes).
        timeout_time (float): Timeout time between message sendings
        meshcore (MeshCore): The sending device
        dst_key (dict): The contact of the device under test

    Returns:
        frames_recvd

    Resoureces:
        https://docs.python.org/3/library/typing.html
	"""
    pass
