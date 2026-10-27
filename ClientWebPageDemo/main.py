from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import wikitohtml


"""
required packages:
pip install fastapi uvicorn jinja2

todo: this may be too wikipedia based. Make it more generic for other apis?
todo: make a page to add in server credentials for direct communication
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
    if q and q.lower() == "pet door":

        # This is an example of what the client will reccieve from server.
        sample_wikitext = """{{Short description|Flap door for pets}}
        [[File:Doggy door exit.JPG|thumb|A dog exiting through a pet door]]
        A ''pet door'' or '''pet flap''' (also referred to in more specific terms, such as '''''cat flap''''', '''cat door''', '''kitty door''', '''dog flap''', '''dog door''', or '''doggy/doggie door''') is a small opening to allow [[pet]]s to enter and exit a building on their own without needing a human to open the door. Originally simple holes, the modern form is a hinged and often spring-loaded panel or flexible flap, and some are electronically controlled. They offer a degree of protection against wind, rain, and larger-bodied intruders entering the dwelling. Similar hatches can let dogs through fences at stiles. A related concept is the '''pet gate''', which is easy for humans to open but acts as a secure pet barrier.

        ==Purpose==
        A pet door is found to be convenient by many owners of companion animals, especially dogs and cats, because it lets the pets come and go as they please, reducing the need for pet-owners to let or take the pet outside manually, and curtailing unwanted behaviour such as loud vocalisation to be let outside, scratching on doors or walls, and (especially in the case of dogs) [[Excretion|excreting]] in the house. They also help to ensure that a pet left outdoors can safely get back into the house unattended, in the case of inclement weather."""

        # Return the raw HTML string directly to the iframe
        generated_html_string = wikitohtml.generatePage(q, sample_wikitext)
        return HTMLResponse(content=generated_html_string)
    return templates.TemplateResponse("embeddedText.html", {"request": request, "search_query": q})


# todo def initiate_connection()

if __name__ == "__main__":
    # Runs the server locally on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)