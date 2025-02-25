import zmq
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www.dnd5eapi.co"    

def fetch_spell_url(url):
    # Append spell url to api home url
    full_url = BASE_URL + url
    response = requests.get(full_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {full_url}")
        return None
    
def load_spells():
    api_url = "https://www.dnd5eapi.co/api/2014/spells"
    response = requests.get(api_url)

    if response.status_code == 200:
        spells = response.json()
        # Fetch URL for each spell
        spell_urls = [spell["url"] for spell in spells["results"]]

        # Use the ThreadPoolExecutor to fetch spell data concurrently for each URL in spell_urls.
        # Create a thread pool with 10 threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 'map' applies the 'fetch_spell_url' function to each URL in 'spell_urls' and returns the results as a list.
            spell_data = list(executor.map(fetch_spell_url, spell_urls))

    return spell_data

def sort_by_name(spell_data):
    spell_data.sort(key=lambda spell:spell["name"])
    return spell_data

def sort_by_level(spell_data, descending=False):
    spell_data.sort(key=lambda spell:spell["level"], reverse=descending)
    return spell_data

def sort_by_class(spell_data, class_name=None):
    class_sorted = []
    if class_name:
        for spell in spell_data:
            for spell_class in spell["classes"]:
                if class_name.lower() == spell_class["name"].lower():
                    class_sorted.append(spell)
    class_sorted = sort_by_name(class_sorted)
    return class_sorted



def handle_request(message, spell_data):
    # Parse Json string and convert it into dictionary
    request_data = json.loads(message)
    sort_by = request_data["sort_by"]
    descending = request_data["descending"]
    class_name = request_data["class_name"]

    if sort_by == "name":
        return json.dumps(sort_by_name(spell_data), indent=4)
    elif sort_by == "level":
        return json.dumps(sort_by_level(spell_data, descending), indent=4)
    elif sort_by == "class":
        return json.dumps(sort_by_class(spell_data, class_name), indent=4)
    else:
        return "invalid choice"
    


def main():
    # Create ZMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)

    # Bind socket to local host
    socket.bind("tcp://localhost:5555")
    
    # Load spells at the beggining of program 
    spell_data = load_spells()

    choice = -1

    while True:
        print("Microservices is waiting for request...")
        message = socket.recv_string()
        print(f"Recieved request: {message}")

        response = handle_request(message, spell_data)
        socket.send_string(response)

main()
