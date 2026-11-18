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
app.state.gateway_name = None

# Where APIs will go
app.include_router(wiki.router)

# Used for connecting device via gui
# todo: what does this do?
class MeshSettings(BaseModel):
    port: str

"""
"""
async def handle_incoming_message(event):
    if event.type in (EventType.CONTACT_MSG_RECV, EventType.CHANNEL_MSG_RECV):
        text = event.payload.get("text", "")

        # This is likely the short prefix (e.g., "!ab12cd34")
        raw_sender_id = event.payload.get("pubkey_prefix", "UnknownGateway")

        # Let's find the FULL public key to use as our mailbox name
        sender_id = raw_sender_id  # Default to raw

        # Look up the contact in the mesh device to get the full key
        if app.state.mesh_connection and app.state.mesh_connection.contacts:
            contact = app.state.mesh_connection.get_contact_by_key_prefix(raw_sender_id)
            if contact:
                sender_id = contact.get("public_key", raw_sender_id)

        # Menu updates
        if text.startswith("Available services:"):
            services_str = text.replace("Available services:", "").strip()
            api_list = [api.strip() for api in services_str.split(",")]
            if not hasattr(app.state, "gateways"):
                app.state.gateways = {}
            app.state.gateways[sender_id] = api_list

        # Drop all other text into the Gateway's Inbox
        else:
            if not hasattr(app.state, "inboxes"):
                app.state.inboxes = {}
            if sender_id not in app.state.inboxes:
                app.state.inboxes[sender_id] = asyncio.Queue()

            # DEBUG PRINT: Prove the mailman is dropping it in the right box!
            print(f"[MAILMAN] Dropping packet into inbox for: {sender_id}")
            app.state.inboxes[sender_id].put_nowait(text)

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
    return templates.TemplateResponse(request=request, name="settings.html")

'''
Let's user input the gateway's credentials
This initiates the connection between the user and gateway
(Sends the OWO that user is on a computer)
'''
@app.get("/addGateway")
async def addGateway(request: Request):
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
    gateway_name = gateway_name.strip()
    request.app.state.gateway_name = gateway_name
    public_key = public_key.strip()
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



if __name__ == "__main__":
    # todo: maybe make host & port a command line argument
    uvicorn.run(app, host="127.0.0.1", port=8000)