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

    if not mesh_connection:
        return HTMLResponse(content="Error: Not connected to Mesh Device.", status_code=500)

    try:
        if not mesh_connection.contacts:
            print("Contacts empty, waiting for mesh to sync...")
            await asyncio.wait_for(mesh_connection.ensure_contacts(), timeout=15.0)

        contact = mesh_connection.get_contact_by_name("Gateway")
        if not contact:
            return HTMLResponse(content="Error: Gateway contact not found on mesh.", status_code=404)

        dest_pub_key = contact.get('public_key')

        # inbox queue for gateway
        if not hasattr(request.app.state, "inboxes"):
            request.app.state.inboxes = {}
        if dest_pub_key not in request.app.state.inboxes:
            request.app.state.inboxes[dest_pub_key] = asyncio.Queue()

        inbox = request.app.state.inboxes[dest_pub_key]

        # Clear out any stale messages from previous searches
        while not inbox.empty():
            inbox.get_nowait()

        # Send commands
        # await mesh_connection.commands.send_msg(dest_pub_key, "OwO")
        # await asyncio.sleep(1)
        await mesh_connection.commands.send_msg(dest_pub_key, "wikipedia")
        await asyncio.sleep(1)
        await mesh_connection.commands.send_msg(dest_pub_key, q)

        # listen for new packets and append
        mesh_reply_text = ""
        print(f"Waiting for Gateway to reply for query: {q}. Inbox ID: {dest_pub_key}")

        first_chunk = await asyncio.wait_for(inbox.get(), timeout=20.0)
        mesh_reply_text += first_chunk
        print(f"[WIKI RECEIVER] Got first packet!")

        while True:
            try:
                chunk = await asyncio.wait_for(inbox.get(), timeout=5.0)
                mesh_reply_text += chunk
                print(f"[WIKI RECEIVER] Appended packet. Total: {len(mesh_reply_text)} chars")
            except asyncio.TimeoutError:
                print("[WIKI RECEIVER] Finished receiving! Generating HTML now...")
                break

    except asyncio.TimeoutError:
        return HTMLResponse(content="Error: Gateway took too long to reply to the initial request.", status_code=504)
    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

    # Generate the HTML from the mesh response
    css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
    generated_html_string = generatePage(q, mesh_reply_text)
    generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")

    return HTMLResponse(content=generated_html_string)

