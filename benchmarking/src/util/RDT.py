"""Ooooh oooooooo, we all love RDT"""

from meshcore import EventType, MeshCore


class RDT:
    async def send_msg(
        self,
        device: MeshCore,
        contact: dict,
        message: str,
        timeout_time: float,
        max_attempts: int | None = None,
    ) -> int:
        """Await an ACK that the DUT knows this devices typ

        Args:
            device (MeshCore): sending device
            contact (dict): contact info of DUT
            msg_type (MsgType): the type of device this device is (sending to
            device under test)
            timeout_time (float): How long to wait for an acknowledgement before
            retrying (seconds)
            max_attempts (int | None): maximum attempts to try doing rdt (this
            not being none => not actually reliable data transfer)
        Return:
            n_attempts (int): The number of attempts before ACK read
        """
        msg_acked = True
        n_attempts = 0
        while not msg_acked:
            if max_attempts and n_attempts >= max_attempts:
                break
            # Send the message and get information about the sent message
            sent_result = await device.commands.send_msg(
                contact,
                message,
            )
            n_attempts += 1
            # Extract the expected acknowledgment code from the message sent event
            if sent_result.type == EventType.ERROR:
                continue

            expected_ack = sent_result.payload["expected_ack"].hex()

            # Wait specifically for this acknowledgment
            result = await device.wait_for_event(
                EventType.ACK,
                attribute_filters={"code": expected_ack},
                timeout=timeout_time,
            )
            if result:
                msg_acked = True

        n_attempts += 1
