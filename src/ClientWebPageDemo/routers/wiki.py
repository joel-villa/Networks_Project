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
    mesh_connection = getattr(request.app.state, "mesh_connection", None)

    # Ensure pending_requests dictionary exists
    if not hasattr(request.app.state, "pending_requests"):
        request.app.state.pending_requests = {}
    pending_requests = request.app.state.pending_requests

    if not mesh_connection:
        return HTMLResponse(content="Error: Not connected to Mesh Device.", status_code=500)

    # Setup the async wait for the mesh reply
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    req_id = str(uuid.uuid4())
    pending_requests[req_id] = future

    try:
        if not mesh_connection.contacts:
            print("Contacts empty, waiting for mesh to sync...")
            await asyncio.wait_for(mesh_connection.ensure_contacts(), timeout=15.0)

        contact = mesh_connection.get_contact_by_name("Gateway")

        if contact:
            dest_pub_key = contact.get('public_key')

            # Send commands with a slight delay so the radio doesn't drop packets
            await mesh_connection.commands.send_msg(dest_pub_key, "OwO")
            await asyncio.sleep(1)
            await mesh_connection.commands.send_msg(dest_pub_key, "wikipedia")
            await asyncio.sleep(1)
            await mesh_connection.commands.send_msg(dest_pub_key, q)
        else:
            pending_requests.pop(req_id, None)
            return HTMLResponse(content="Error: Gateway contact not found on mesh.", status_code=404)

        # Wait for the listener in main.py to resolve the future
        print(f"Waiting for Gateway to reply for query: {q}...")
        mesh_reply_text = await asyncio.wait_for(future, timeout=45.0)

    except asyncio.TimeoutError:
        pending_requests.pop(req_id, None)
        return HTMLResponse(content="Error: Gateway took too long to reply.", status_code=504)
    except Exception as e:
        pending_requests.pop(req_id, None)
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

    # Generate the HTML from the mesh response
    css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
    generated_html_string = generatePage(q, mesh_reply_text)
    generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")

    return HTMLResponse(content=generated_html_string)

