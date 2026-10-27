from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import uvicorn

"""
required packages:
pip install fastapi uvicorn jinja2
"""

app = FastAPI()

# Tell FastAPI where to find the HTML files
templates = Jinja2Templates(directory="clientPages")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/errorScreen")
async def about(request: Request):
    return templates.TemplateResponse("errorScreen.html", {"request": request})

@app.get("/wikiSearch")
async def dashboard(request: Request):
    return templates.TemplateResponse("wikiSearch.html", {"request": request})

@app.get("/embeddedText")
async def embedded(request: Request):
    return templates.TemplateResponse("embeddedText.html", {"request": request})

if __name__ == "__main__":
    # Runs the server locally on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)