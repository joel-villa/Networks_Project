import asyncio
import uuid

import requests
from fastapi import Form
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.client.services.wikitohtml import generatePage

router = APIRouter()
templates = Jinja2Templates(directory="src/ClientWebPageDemo/clientPages")


"""
Gets the gateway's name and public key
"""
async def _get_mesh_target(app_state, gateway_name: str):
    mesh = getattr(app_state, "mesh_connection", None)
    if not mesh:
        raise ValueError("Not connected to Mesh Device.")

    if not mesh.contacts:
        await asyncio.wait_for(mesh.ensure_contacts(), timeout=5.0)

    contact = mesh.get_contact_by_name(gateway_name)
    if not contact:
        raise ValueError(f"Gateway '{gateway_name}' not found on mesh.")

    return mesh, contact.get('public_key')

"""
Creates or clears the async queue for a specific gateway.
"""
def _prepare_inbox(app_state, pub_key: str):
    if not hasattr(app_state, "inboxes"):
        app_state.inboxes = {}
    if pub_key not in app_state.inboxes:
        app_state.inboxes[pub_key] = asyncio.Queue()

    inbox = app_state.inboxes[pub_key]
    while not inbox.empty():
        inbox.get_nowait()
    return inbox


"""
 Waits for the first chunk, then collects subsequent chunks until timeout.
"""
async def _collect_mesh_response(inbox) -> str:
    mesh_reply_text = ""

    # Wait up to 5s for the very first response packet
    first_chunk = await asyncio.wait_for(inbox.get(), timeout=5.0)
    mesh_reply_text += first_chunk

    # Wait up to 5s for subsequent packets; break when they stop coming
    while True:
        try:
            chunk = await asyncio.wait_for(inbox.get(), timeout=5.0)
            mesh_reply_text += chunk
        except asyncio.TimeoutError:
            break

    return mesh_reply_text


"""
Embedded text handles the iframe that posts the wikipedia results (or the default waiting screen) 
"""
@router.get("/embeddedText")
async def embeddedText(request: Request, q: str = None):
    gateway = getattr(request.app.state, "gateway_name", None)

    if not gateway:
        return HTMLResponse(content="Error: No gateway connected.", status_code=400)

    try:
        mesh, pub_key = await _get_mesh_target(request.app.state, gateway)

        if not q:
            await mesh.commands.send_msg(pub_key, "wikipedia")
            return HTMLResponse(content='<div style="font-family: sans-serif; padding: 20px;">Ready for Wikipedia search.</div>')
        q = q.title()
        inbox = _prepare_inbox(request.app.state, pub_key)

        await mesh.commands.send_msg(pub_key, q)
        mesh_reply_text = await _collect_mesh_response(inbox)

    except asyncio.TimeoutError:
        return HTMLResponse(content="Error: Gateway timed out.", status_code=504)

    except ValueError as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=400)

    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

    # Generate the HTML from the mesh response
    css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
    generated_html_string = generatePage(q, mesh_reply_text)
    generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")

    return HTMLResponse(content=generated_html_string)


@router.get("/wikiSearch")
async def searchWiki(request: Request):
    return templates.TemplateResponse(request=request, name="wikiSearch.html")
