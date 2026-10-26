def tagify(content: str, type: str):
    return f"<{type}>{content}</{type}>"

def processChunk(wikitextChunk: str) -> str:
    result = ""
    paragraphs = wikitextChunk.split("\n")
    for p in paragraphs:
        para = p.strip();
        if para[0:2] == "==":
            result += tagify(para[2: len(para) - 2], "h2")
        else:
            result += tagify(para, "p")
    return result

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
    print(generatePage("Pet door", """==Purpose==
    A pet door is found to be convenient by many owners of companion animals, especially dogs and cats, because it lets the pets come and go as they please, reducing the need for pet-owners to let or take the pet outside manually, and curtailing unwanted behaviour such as loud vocalisation to be let outside, scratching on doors or walls, and (especially in the case of dogs) [[Excretion|excreting]] in the house. They also help to ensure that a pet left outdoors can safely get back into the house unattended, in the case of inclement weather.

    ==Features==
    [[File:Cat flap.jpg|thumb|A cat flap in action]]
    The simplest type are bottom-weighted flaps hung from the top of the opening, which swing shut on their own, but may be spring-aided to increase wind resistance. These flaps often feature magnets around the edges to help keep the door closed against weather and wind. Some pet doors, made of rigid materials, have side-mounted hinges and swing open like saloon doors, and usually have a spring or other contrivance to force their closure after the pet has gone through. Another door type, also rigid, may hinge at the top and simply rely on gravity to swing it down to where magnetism may engage to hold it properly closed. The rigid materials used are often made from plastic for the framing, and for a transparent door element, high density [[polystyrene]], or better such as acrylics like plexiglass. The tolerances possible with rigid form allow fitting the door and frame with a low friction weather seal designed to block air flow without binding caused by friction around the sealing perimeter. This may be achieved with a synthetic material resembling a sparse high-piled velvet with fibers stiff and elastic enough to resist matting.
    Another common feature is an adjustable catch to restrict the opening of the device to either one direction or the other; for example, to allow the pet to come in for the night, but not go out again until the owner releases the catch the next morning. Some pets, mostly cats with their retractile claws and flexible paws, learn to circumvent one-way pet doors, especially the "flap-within-flap" design."""))

if __name__ == "__main__":
    main()