"""
User object will be directly interfacing with the user
- Handles the requesting the type of API (API Object)
- And other
- Send state to the gateway
- If multiple results, send the top n article names w/ one sentence
- This is doing all of the querying/section and selection
"""

class user
    def run():
        try:
            while True:
                async def handle_user_message(event):
                    payload =event.payload
                    message = payload.get("text","")
                    
                    reply = makeReply(message)
                    success = meshcore.commands.send(reply)
                    # todo, add error checking for this

                