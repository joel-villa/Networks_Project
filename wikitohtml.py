## TODO, check out all wikitext formatting, do them all?

def formatParagraph(paragraphText: str) -> str:
    result = ""
    phrases = paragraphText.split("'''")
    for i in range(len(phrases)):
        if i % 2 == 1:
            result += tagify(phrases[i], "b")
        else:
            result += phrases[i];
    links = result.split("[[")
    result = ""
    for i in range(len(links)):
        if i % 2 == 1:
            endLink = links[i].find("]]")
            linkBody = links[i][0: endLink]
            linkRemainder = links[i][endLink + 2: len(links[i]) - 1]
            result += f"{formatLink(linkBody)}{linkRemainder}"
        else:
            result += links[i]
    return result

def formatLink(wikitextLink: str) -> str:
    parts = wikitextLink.split("|")
    if len(parts) == 1:
        return tagifyArgs(wikitextLink, "a", "href", parts[0])
    elif len(parts) == 2:
        return tagifyArgs(parts[1], "a", "href", parts[0])
    elif len(parts) == 3:
        return f"Image '{parts[0]}' of '{parts[2]}'"

def tagify(content: str, type: str) -> str:
    if type == "p":
        return f"<{type}>{formatParagraph(content)}</{type}>"
    return f"<{type}>{content}</{type}>"

def tagifyArgs(content: str, type: str, argName: str, argVal: str) -> str:
    return f"<{type} {argName}='{argVal}'>{formatParagraph(content)}</{type}>"

def processChunk(wikitextChunk: str) -> str:
    result = ""
    paragraphs = wikitextChunk.split("\n")
    for p in paragraphs:
        para = p.strip();
        if para[0] == para[len(para) - 1] == "=":
            result += makeHeader(para)
        else:
            result += tagify(para, "p")
    return result

def makeHeader(headerStr: str) -> str:
    hLevel = headerStr.count("=") / 2
    return tagify(headerStr.replace("=",""), f"h{int(hLevel)}")

def translate(wikitext: str) -> str: 
    result = ""
    chunks = wikitext.split("\n\n")
    for chunk in chunks:
        result += processChunk(chunk)
    return result;

def generatePage(title: str, wikitext: str):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimal HTML Document</title>
</head>
<body>
{tagify(title, "h1")}
{translate(wikitext)}
</body>
</html>"""

def main():
    print(generatePage("Pet door", """{{Short description|Flap door for pets}}
[[File:Doggy door exit.JPG|thumb|A dog exiting through a pet door]]
A '''pet door''' or '''pet flap''' (also referred to in more specific terms, such as '''cat flap''', '''cat door''', '''kitty door''', '''dog flap''', '''dog door''', or '''doggy/doggie door''') is a small opening to allow [[pet]]s to enter and exit a building on their own without needing a human to open the door.  Originally simple holes, the modern form is a hinged and often spring-loaded panel or flexible flap, and some are electronically controlled.  They offer a degree of protection against wind, rain, and larger-bodied intruders entering the dwelling. Similar hatches can let dogs through fences at stiles. A related concept is the '''pet gate''', which is easy for humans to open but acts as a secure pet barrier.

==Purpose==
A pet door is found to be convenient by many owners of companion animals, especially dogs and cats, because it lets the pets come and go as they please, reducing the need for pet-owners to let or take the pet outside manually, and curtailing unwanted behaviour such as loud vocalisation to be let outside, scratching on doors or walls, and (especially in the case of dogs) [[Excretion|excreting]] in the house. They also help to ensure that a pet left outdoors can safely get back into the house unattended, in the case of inclement weather.

==Features==
[[File:Cat flap.jpg|thumb|A cat flap in action]]
The simplest type are bottom-weighted flaps hung from the top of the opening, which swing shut on their own, but may be spring-aided to increase wind resistance. These flaps often feature magnets around the edges to help keep the door closed against weather and wind. Some pet doors, made of rigid materials, have side-mounted hinges and swing open like saloon doors, and usually have a spring or other contrivance to force their closure after the pet has gone through. Another door type, also rigid, may hinge at the top and simply rely on gravity to swing it down to where magnetism may engage to hold it properly closed. The rigid materials used are often made from plastic for the framing, and for a transparent door element, high density [[polystyrene]], or better such as acrylics like plexiglass. The tolerances possible with rigid form allow fitting the door and frame with a low friction weather seal designed to block air flow without binding caused by friction around the sealing perimeter. This may be achieved with a synthetic material resembling a sparse high-piled velvet with fibers stiff and elastic enough to resist matting.

Another common feature is an adjustable catch to restrict the opening of the device to either one direction or the other; for example, to allow the pet to come in for the night, but not go out again until the owner releases the catch the next morning. Some pets, mostly cats with their retractile claws and flexible paws, learn to circumvent one-way pet doors, especially the "flap-within-flap" design.

Most also have a locking mechanism of some kind, and can be closed off by sliding a rigid plate into parallel rails on the left and right of the interior side of the pet door, useful during bad weather or when the owners are traveling with their pets.

Pet doors are generally designed to be safe for any type of pet.  The panels are often designed with soft [[Polyvinyl chloride|vinyl]] that does not trap or injure the animal. Cheap, easily replaceable pet doors are made from plastic and may not always be robust enough for large, boisterous pets."""))

if __name__ == "__main__":
    main()