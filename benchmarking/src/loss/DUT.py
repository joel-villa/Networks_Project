"""The device under test (DUT) is expected to have one mesh node, i.e. it
needs a thread and is capable of sending and recieving through that mesh node.
Also, the DUT needs a map of contacts to contacts (contacts to recv and send to
accordingly)"""

from meshcore.events import Event

class DUT:
    """The DUT test class"""

    # Incoming messages are gotten using the public key prefix, outgoing using the contact dict
    mesh_dict: dict[str, dict]
    #TODO: other variables

    def __init__(
        self,
    ) -> None:
        raise NotImplementedError

    def __handle_message(
        self,
        received_msg: Event,
    ) -> None:
        """Handle a message from a sender, update the receiver

        Args:
            received_msg (Event): The message recieved by this device
        """
        raise NotImplementedError

    def __handshake(
        self
    ) -> None:
        raise NotImplementedError
