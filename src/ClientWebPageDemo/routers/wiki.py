import asyncio
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.client.services.wikitohtml import generatePage

# 1. Create a router instance
router = APIRouter()

# 2. Point to your templates
templates = Jinja2Templates(directory="src/ClientWebPageDemo/clientPages")


@router.get("/wikiSearch")
async def searchWiki(request: Request):
    return templates.TemplateResponse(request=request, name="wikiSearch.html")


@router.get("/embeddedText")
async def embeddedText(request: Request, q: str = None):
    if not q:
        return templates.TemplateResponse(request=request, name="embeddedText.html", context={"search_query": q})

    q = q.title()

    # Access the global state variables from the request object
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
        # Send the mesh command (ensure CHANNEL_IDX is accessible or passed in)
        await mesh_connection.commands.send_chan_msg(0, f"{q}")

        # Wait for the reply from the background subscriber
        # mesh_reply_text = await asyncio.wait_for(future, timeout=45.0)
        mesh_reply_text = "lalalalal"
    except asyncio.TimeoutError:
        del pending_requests[req_id]
        return HTMLResponse(content="Error: Mesh timeout.", status_code=504)
    except Exception as e:
        return HTMLResponse(content=f"Error: {e}", status_code=500)

    # Generate the HTML from the mesh response
    css_string = '<link rel="stylesheet" href="/static/wikipedia.css">'
    generated_html_string = generatePage(q, mesh_reply_text)
    generated_html_string = generated_html_string.replace("</head>", f"{css_string}\n</head>")

    return HTMLResponse(content=generated_html_string)