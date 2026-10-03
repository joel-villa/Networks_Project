import asyncio
from googlesearch import search
from meshcore import MeshCore, EventType
import csv
import requests
import json



PORT = "/dev/ttyUSB0"
CHANNEL_IDX = 0
CHANNEL_NAME = "MeshedUp"
USER_AGENT = "pleaseWiki"
CHANNEL_SECRET = bytes.fromhex("aa27c63feeacd8e835d02d243a17c409")
MAX_MSG_LEN = 130 # TODO or is it 150 

options = ['Knock Knock', 'google', 'ip', 'wiki']
setup = ["Lettuce", "Boo", "Tank", "Interrupting cow"]
punch = [
    "Lettuce in, it's cold out here!",
    "Don't cry, it's just a joke!",
    "You're welcome!",
    "MOO!",
]

users = {}

def searchWikipedia(query: str, sentences: int = 2) -> str:
    
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": 1,
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "redirects": 1,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=8,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        if not pages:
            return "No Wikipedia results found"
        page = next(iter(pages.values()))
        extract = page.get("extract", "").strip()
        if not extract:
            return f"{page.get('title', query)}: no summary available"
        short = " ".join(extract.replace("\n", " ").split(". ")[:sentences])
        return f"{page['title']}: {short}"
    except Exception as e:
        print(f"Wiki issue: {type(e).__name__}: {e}")
        return "Wikipedia lookup failed, try again"



def menuText() -> str:
    return f"reply 0 for {options[0]} or 1 for {options[1]} or say which option"


def handleNewUser(user: str, text: str) -> str:
    choice = text.strip().lower()
    if choice == '0' or choice == "knock knock":
        users[user] = {"wants": 0, "step": 0, "joke": 0}
        return f"Hello {user}! I see you want {options[0]}. Knock knock!"
    elif choice == '1' or choice == "google":
        users[user] = {"wants": 1}
        return f"Hello {user}! I see you want {options[1]}. What should I search?"
    elif choice == '2' or choice == "ip":
        users[user] = {"wants":2}
        return f"Hello {user}! I see you want {options[2]}. Who should I search?"
    elif choice == '3' or choice == "wiki":
        users[user] = {"wants":3}
        return f"Hello {user}! I see you want {options[3]}. What should I search?"
    else:
        return f"I don't understand. {menuText()}"


# def searchGoogle(query: str) -> str:
#     print(f"attempting to search with {query}")
#     try:
#         for result in search(query, advanced=True):
#             print(f"{result.title}: {result.description}")
#             return f"{result.title}: {result.description}"
#     except Exception as e:
#         print(f"Search failed: {e}")
#         return "Search failed, try again"
#     return "No results found"
from googlesearch import search

def split_message(text):
    
    chunks = []
    while len(text) > MAX_MSG_LEN :
        
        breaker = text.rfind(' ', 0, MAX_MSG_LEN )
        if breaker == -1:
            breaker = MAX_MSG_LEN 
        
        chunks.append(text[:breaker])
        text = text[breaker:].lstrip() 
    
    if text:
        chunks.append(text)
    return chunks

def searchGoogle(query: str) -> str:
    print(f"Attempting to search with: {query}")

    try:
        results = search(
            query,
            num_results=5, ## Or whatever we agree on
            lang="en"
        )

        for index, url in enumerate(results, start=1):
            print(f"{index}. {url}")

    except Exception as e:
        print(f"Issue: {type(e).__name__}: {e}")

    return ""
    
def queryIp() -> str:
    try:
        print("here")
        url = 'https://api.abuseipdb.com/api/v2/check'

        querystring = {
            'ipAddress': '118.25.6.39',
            'maxAgeInDays': '90'
        }

        headers = {
            'Accept': 'application/json',
            'Key': '39a9ed7e3fafdd963eaf60612ea8bafbebf1894a42f4e2ba6d92c7403bd0cda11adbd84dc3f38a5a'
        }
        print("here 2")
        response = requests.request(method='GET', url=url, headers=headers, params=querystring)

        # Formatted output
        decodedResponse = json.loads(response.text)
        print (json.dumps(decodedResponse, sort_keys=True, indent=4))
        return decodedResponse
    except Exception as e:
        print(f"Issue: {type(e).__name__}: {e}")
    return ""

    



def makeKnock(text: str, step: int, joke: int) -> str | None:
    text = text.lower()
    if step == 0 and ("who's" in text or "whos" in text or "who is" in text  or "who’s" in text):
        return setup[joke]
    elif step == 1 and 'who' in text:
        return punch[joke]
    return None


async def make_reply(user: str, text: str) -> str | None:
    """Parse te responce"""
    print(text)
    text = text.strip()

    if text.lower() in ("menu", "stop", "exit"):
        users.pop(user, None)
        return f"Bye {user}! {menuText()}"

    state = users.get(user)
    if state is None:
        return handleNewUser(user, text)

    if state["wants"] == 0:
        reply = makeKnock(text, state["step"], state["joke"])
        if reply is None:
            if state["step"] == 0:
                return "You're supposed to say: who's there?"
            return f"You're supposed to say: {setup[state['joke']]} who?"
        if state["step"] == 0:
            state["step"] = 1
        else:
            state["step"] = 0
            state["joke"] = (state["joke"] + 1) % len(setup)
            reply += " Knock knock!"
        return reply

    if state["wants"] == 1:
        return await asyncio.to_thread(searchGoogle, text)
    
    if state["wants"] ==2: 
        return queryIp()

    if state["wants"] ==3: 
        return searchWikipedia(text)

    return None


async def main():
    mc = await MeshCore.create_serial(PORT)

    result = await mc.commands.set_channel(CHANNEL_IDX, CHANNEL_NAME, CHANNEL_SECRET)
    if result.type == EventType.ERROR:
        print(f"Failed to set channel: {result.payload}")
        await mc.disconnect()
        return
    print(f"Channel {CHANNEL_IDX} configured as '{CHANNEL_NAME}'")
    await mc.commands.send_chan_msg(CHANNEL_IDX, 'Wellcome! ' + menuText())

    async def handle_channel_message(event):
        payload = event.payload
        if payload.get("channel_idx") != CHANNEL_IDX:
            return

        text = payload.get("text", "")
        # in a channal it will put the name before the message so we break it up by the :
        if ':' in text:
            user, text = text.split(':', 1)
            user = user.strip()
        else:
            user = "unknown"
        text = text.strip()
        print(f"[chan {payload['channel_idx']}] {user}: {text}")
        print(f"Payload {payload}")

        reply = await make_reply(user, text)
        if(len(reply)>MAX_MSG_LEN):
            parts = split_message(reply)
            for part in parts:
                if part:
                    await mc.commands.send_chan_msg(CHANNEL_IDX, part)
        else:
            send_result = await mc.commands.send_chan_msg(CHANNEL_IDX, reply)

        

            
        print(reply)
        # reply1 = reply[:MAX_MSG_LEN]
        # reply2 = reply[MAX_MSG_LEN:]
        
        #send_result = await mc.commands.send_chan_msg(CHANNEL_IDX, reply)
        if send_result.type == EventType.ERROR:
            print(f"Failed to send reply: {send_result.payload}")
        else:
            print(f"Sent: {reply1}")

    async def handle_ack(event):
        print("Message acknowledged!")

    mc.subscribe(EventType.CHANNEL_MSG_RECV, handle_channel_message)
    mc.subscribe(EventType.ACK, handle_ack)

    await mc.start_auto_message_fetching()

    await mc.commands.send_advert(flood=True)

    print("Connected ")
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await mc.stop_auto_message_fetching()
        await mc.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass