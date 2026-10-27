from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import uvicorn

"""
required packages:
pip install fastapi uvicorn jinja2

Future todo: make a page to add in server credentials for direct communication
"""

app = FastAPI()
# HTML pages
templates = Jinja2Templates(directory="clientPages")

@app.get("/")
async def menu(request: Request):
    # todo: will need code to try to initiate the connection with client
    # if wikipedia Api is pressed -> initiate_wikipedia_connection()
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/errorScreen")
async def error(request: Request):
    # todo: will need code to try to initiate the connection with client
    # if try_again -> initiate_wikipedia_connection()
    return templates.TemplateResponse("errorScreen.html", {"request": request})

@app.get("/wikiSearch")
async def searchWiki(request: Request):
    return templates.TemplateResponse("wikiSearch.html", {"request": request})

@app.get("/embeddedText")
async def embeddedText(request: Request, q: str = None):
    # todo: the code here changes the iframe content
    return templates.TemplateResponse("embeddedText.html", {"request": request, "search_query": q})


# todo def initiate_connection()

if __name__ == "__main__":
    # Runs the server locally on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)