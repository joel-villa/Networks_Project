"""
Main Class that will handle most of the server side functionality.
- Contains the clients and will accecpt connections and will spawn new connections
- Will connect users to their desired APIs

- Listen for new connections will create new threads for each client (Client object)
"""
import os
import threads
import meshcore from MeshCore
from dotenv import load_dotenv

load_dotenv()
#replace your path in the .env file (make a .env file(atroot))
path=os.getenv("PORT")   
print(path)

def handleNewUser

meshcore = await MeshCore.create_serial(path)

def main():
    while True:
        # accept connectsions, call user py with thread
