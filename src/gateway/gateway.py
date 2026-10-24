"""
Main Class that will handle most of the server side functionality.
- Contains the clients and will accecpt connections and will spawn new connections
- Will connect users to their desired APIs

- Listen for new connections will create new threads for each client (Client object)
"""

from meshcore import MeshCore


class Gateway:
    """The client handler"""

    device: MeshCore

    def __init__(self, device: MeshCore) -> None:
        self.device = device
