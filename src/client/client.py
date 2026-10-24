"""
Client Object for the server.
Handles:
- Makes it pretty
- Take in .wiki files for the server to receive for user
- TODO: What about non wiki files?
- Display as HTML files
- Only interface through the html?
- Cannot interface with meshcore app and this app at the same time
- Connect via terminal
"""


class Client:
    """The latency test class"""

    api_type: int
    user_name: str
    state: int

    def __init__(self, api_type: int, user_name: str, state: int) -> None:
        self.api_type = api_type
        self.user_name = user_name
        self.state = state
