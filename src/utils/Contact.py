
load_dotenv()
path = os.getenv("MESH_PATH")
meshcore = await MeshCore.create_serial(path)
meshcore_contacts: dict[str, str]
with open("secrets.json") as json_file:
            data = json.load(json_file)
            meshcore_contacts = data[MESHCORE_CONTACT_INFO]  
for public_key, adv_name in meshcore_contacts.items():
    contact_data = {
        "public_key": public_key,
        "adv_name": adv_name,
        "type": 2
    }
    
    await meshcore.commands.add_contact(contact_data)
 