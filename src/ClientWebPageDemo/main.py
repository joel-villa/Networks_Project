from os.path import samefile

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from src.client.services.wikitohtml import generatePage
from src.client.services.getWikitext import getWikitext
from meshcore import EventType, MeshCore
import asyncio

# Add APIs here!
from src.ClientWebPageDemo.routers import wiki


"""
required packages:
pip install fastapi uvicorn jinja2 requests

run from project root:
python3 -m src.ClientWebPageDemo.main

todo: make a page to add in server credentials for direct communication
"""

app = FastAPI()
# HTML pages
app.mount("/static", StaticFiles(directory="src/ClientWebPageDemo/static"), name="static")
templates = Jinja2Templates(directory="src/ClientWebPageDemo/clientPages")

# current mesh device state
app.state.mesh_connection = None
app.state.pending_requests = {}

# Where APIs will go
app.include_router(wiki.router)

# Used for connecting device via gui
# todo: what does this do?
class MeshSettings(BaseModel):
    port: str


async def handle_incoming_message(event):
    if event.type == EventType.CONTACT_MSG_RECV:
        text = event.payload.get("text", "")

        # Todo: Fix this
        sender_name = event.payload.get("sender_name", "UnknownGateway")

        if text.startswith("Available services:"):
            # Strip String
            services_str = text.replace("Available services:", "").strip()

            # Split by comma into a list: ['wikipedia', 'duckduckgo', 'weather']
            api_list = [api.strip() for api in services_str.split(",")]

            # Save to app state so the Menu route can see it
            if not hasattr(app.state, "gateways"):
                app.state.gateways = {}

            app.state.gateways[sender_name] = api_list
            print(f"Updated services for {sender_name}: {api_list}")

"""
Uses input from html settings page for device port
:param settings:
:return:
"""
@app.post("/connect_mesh_device")
async def connect_mesh(settings: MeshSettings):
    if app.state.mesh_connection:
        try:
            await app.state.mesh_connection.disconnect()
        except Exception:
            pass

    try:
        # Connect to the new port
        app.state.mesh_connection = await MeshCore.create_serial(settings.port)

        # Listener
        await app.state.mesh_connection.connect()
        app.state.mesh_connection.subscribe(EventType.CONTACT_MSG_RECV, handle_incoming_message)
        await app.state.mesh_connection.start_auto_message_fetching()

        return {"status": "success", "message": f"Successfully connected to {settings.port}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


"""
Menu that shows all of the APIs from the servers. 
Also, shows user mesh device status. 
For example:
Mesh Node Status: Connected or Disconnected
Wikipedia [Gateway1]
NASA [Gateway1]
Wikipedia [Gateway2]
"""
@app.get("/")
async def menu(request: Request):
    # Check if the user's mesh device is connected
    mesh = getattr(request.app.state, "mesh_connection", None)
    mesh_status = "Connected" if mesh else "Disconnected"

    # Retrieve the known gateways and their APIs
    # Expected structure: {"Gateway1": ["wikipedia", "weather"], "Gateway2": ["nasa"]}
    gateways = getattr(request.app.state, "gateways", {})

    # Pass these variables to the index.html template using 'context'
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "mesh_status": mesh_status,
            "gateways": gateways
        }
    )

"""
Connects the mesh device to this application.
Requires the device port. 
"""
@app.get("/settings")
async def settings(request: Request):
    # Todo this this should be done in python!
    return templates.TemplateResponse(request=request, name="settings.html")

'''
Let's user input the gateway's credentials
This initiates the connection between the user and gateway
(Sends the OWO that user is on a computer)
'''
@app.get("/addGateway")
async def addGateway(request: Request):
    # todo: will try to initiate the connection with gateway
    # todo: sends OWO to gateway to indentify as computer
    # Gateway should send back a list of supported APIs
    # todo: this is create the list of APIs seen on the MENU page
    return templates.TemplateResponse(request=request, name="add_gateway.html")


"""
# todo: will try to initiate the connection with gateway
# todo: sends OWO to gateway to indentify as computer
Gateway should send back a list of supported APIs
# todo: this is create the list of APIs seen on the MENU page
"""
@app.post("/addGateway")
async def connect_to_gateway(
        request: Request,
        gateway_name: str = Form(...),
        public_key: str = Form(...)
):
    # get te existing connection from the app state
    mesh = getattr(request.app.state, "mesh_connection", None)

    if not mesh:
        return {"error": "No mesh device connected. Please connect your device first."}

    try:
        # Ensure contacts are synchronized before searching
        await asyncio.wait_for(mesh.ensure_contacts(), timeout=30.0)

        # Look up the gateway by name
        contact = mesh.get_contact_by_name(gateway_name)

        # Fallback: Look up by public key
        if not contact and mesh.contacts:
            for node_id, contact_obj in mesh.contacts.items():
                if isinstance(contact_obj, dict) and contact_obj.get('public_key') == public_key:
                    contact = contact_obj
                    break

        if not contact:
            return {"error": f"Could not find {gateway_name} on the mesh network."}

        # Extract the public key
        dest_pub_key = contact.get('public_key')

        if not dest_pub_key:
            return {"error": "Gateway found, but missing a public key."}

        # Send OwO
        result = await mesh.commands.send_msg(dest_pub_key, "OwO")

        # Check if the mesh radio reported an error sending the message
        if result.type == EventType.ERROR:
            return {"error": f"Radio error sending message: {result.payload}"}

        return {"status": "success", "message": f"OWO sent to {gateway_name}"}

    except asyncio.TimeoutError:
        return {"error": "Timed out waiting for mesh contacts to synchronize."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}




@app.get("/errorScreen")
async def error(request: Request):
    # todo: is this needed?
    return templates.TemplateResponse(request=request, name="errorScreen.html")


# @app.get("/wikiSearch")
# async def searchWiki(request: Request):
#     # return templates.TemplateResponse("wikiSearch.html", {"request": request})
#     return templates.TemplateResponse(request=request, name="wikiSearch.html")
#
#
# @app.get("/embeddedText")
# async def embeddedText(request: Request, q: str = None):
#
#
#
#
#     if q and q.lower() == "pet door":
#         q = q.title()
#
#         # todo: this should be sent from the server
#         #  This is an example of what the client will reccieve from server.
#         sample_wikitext = """{{Short description|Flap door for pets}}
#         [[File:Doggy door exit.JPG|thumb|A dog exiting through a pet door]]
#         A ''pet door'' or '''pet flap''' (also referred to in more specific terms, such as '''''cat flap''''', '''cat door''', '''kitty door''', '''dog flap''', '''dog door''', or '''doggy/doggie door''') is a small opening to allow [[pet]]s to enter and exit a building on their own without needing a human to open the door. Originally simple holes, the modern form is a hinged and often spring-loaded panel or flexible flap, and some are electronically controlled. They offer a degree of protection against wind, rain, and larger-bodied intruders entering the dwelling. Similar hatches can let dogs through fences at stiles. A related concept is the '''pet gate''', which is easy for humans to open but acts as a secure pet barrier.
#         ==Purpose==
#         A pet door is found to be convenient by many owners of companion animals, especially dogs and cats, because it lets the pets come and go as they please, reducing the need for pet-owners to let or take the pet outside manually, and curtailing unwanted behaviour such as loud vocalisation to be let outside, scratching on doors or walls, and (especially in the case of dogs) [[Excretion|excreting]] in the house. They also help to ensure that a pet left outdoors can safely get back into the house unattended, in the case of inclement weather."""
#
#         # turn the wiki format into html
#         css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
#         generated_html_string = (generatePage(q, sample_wikitext))
#         generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")
#         return HTMLResponse(content=generated_html_string)
#
#     return templates.TemplateResponse(request=request,name="embeddedText.html",context={"search_query": q}
#     )





if __name__ == "__main__":
    # Runs the server locally on port 8000
    # mc = await MeshCore.create_serial(PORT)
    # todo: maybe make host & port a command line argument
    uvicorn.run(app, host="127.0.0.1", port=8000)