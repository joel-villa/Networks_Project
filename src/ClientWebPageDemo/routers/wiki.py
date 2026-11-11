import asyncio
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.client.services.wikitohtml import generatePage

router = APIRouter()
templates = Jinja2Templates(directory="src/ClientWebPageDemo/clientPages")

@router.get("/wikiSearch")
async def searchWiki(request: Request):
    return templates.TemplateResponse(request=request, name="wikiSearch.html")

@router.get("/embeddedText")
async def embeddedText(request: Request, q: str = None):
    if not q:
        return templates.TemplateResponse(request=request, name="embeddedText.html", context={"search_query": q})

    q = q.title()
    mesh_connection = request.app.state.mesh_connection
    pending_requests = request.app.state.pending_requests

    if not mesh_connection:
        return HTMLResponse(content="Error: Not connected to Mesh Device.", status_code=500)

    # Setup the async wait for the mesh reply
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    req_id = str(uuid.uuid4())
    pending_requests[req_id] = future

    try:
        # Force the mesh connection to sync contacts if it's currently empty
        if not mesh_connection.contacts:
            print("Contacts empty, waiting for mesh to sync...")
            # Wait up to 15 seconds for the contacts to populate
            await asyncio.wait_for(mesh_connection.ensure_contacts(), timeout=15.0)

        contact = mesh_connection.get_contact_by_name("Gateway")

        if contact:
            await mesh_connection.commands.send_msg(contact, f"OwO")
            await mesh_connection.commands.send_msg(contact, f"wikipedia")
            await mesh_connection.commands.send_msg(contact, f"{q}")
        else:
            del pending_requests[req_id]
            print("Contact not found after sync!")
            return HTMLResponse(content="Error: Gateway contact not found on mesh.", status_code=404)

        # Wait for the reply from the background subscriber
        mesh_reply_text = await asyncio.wait_for(future, timeout=45.0)

    except asyncio.TimeoutError:
        del pending_requests[req_id]
        return HTMLResponse(content="Error: Mesh timeout while syncing contacts or waiting for reply.", status_code=504)

    # Generate the HTML from the mesh response
    css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
    generated_html_string = generatePage(q, mesh_reply_text)
    generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")

    return HTMLResponse(content=generated_html_string)