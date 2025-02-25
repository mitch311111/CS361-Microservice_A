import zmq
import requests
import json
from concurrent.futures import ThreadPoolExecutor

"""
Message format from main program...
message = {
                "sort_by": (The method of sorting. can either be name, level, or class)
                "descending": (Boolean where if true = descending and false = ascending. Otherwise None is passed if not sorting by level)
                "class_name": (class name given by input from the user. Otherwise None is passed if not sorting by class.)
            }

or

message = {end_program: true} if the main program is signaling to end the program
"""

# Home url of the API website
BASE_URL = "https://www.dnd5eapi.co"    

# Fetches spell data from the API for a single spell
def fetch_spell_url(url):
    # Append spell url to api home url
    full_url = BASE_URL + url
    response = requests.get(full_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {full_url}")
        return None

# load all spells by fetching each spells url form the API.
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

# Sort the list of spells by name (alphabetically).
def sort_by_name(spell_data):
    spell_data.sort(key=lambda spell:spell["name"])
    return spell_data

# Sort the list of spells by level. Either ascending or descending order.
def sort_by_level(spell_data, descending=False):
    spell_data.sort(key=lambda spell:spell["level"], reverse=descending)
    return spell_data

# Sort the list of spells by class name. Returns only the spells with the given class.
def sort_by_class(spell_data, class_name=None):
    class_sorted = []
    if class_name:
        for spell in spell_data:
            for spell_class in spell["classes"]:
                if class_name.lower() == spell_class["name"].lower():
                    class_sorted.append(spell)
    class_sorted = sort_by_name(class_sorted)
    return class_sorted

# Process incoming sorting/filtering requests. Returns the result in Json format.
def handle_request(message, spell_data):
    # Parse Json string and convert it into a python dictionary
    request_data = json.loads(message)

    if "end_program" in request_data and request_data["end_program"]:
        print("Termination signal recieved, Ending program.")
        return "terminate"

    # Extract sorting/filtering criteria from the request
    sort_by = request_data["sort_by"]
    descending = request_data["descending"]
    class_name = request_data["class_name"]

    # Sort spells by name
    if sort_by == "name":
        return json.dumps(sort_by_name(spell_data), indent=4)
    
    # Sort spells by level
    elif sort_by == "level":
        return json.dumps(sort_by_level(spell_data, descending), indent=4)

    # Sort spells by class
    elif sort_by == "class":
        return json.dumps(sort_by_class(spell_data, class_name), indent=4)
    
    # Otherwise return an error message
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

    while True:
        # Wait for a request from the main program
        print("Microservices is waiting for request...")

        # Recieve a message (Json string) form the client
        message = socket.recv_string()
        print(f"Recieved request: {message}")

        # Process the request and get the response
        response = handle_request(message, spell_data)

        # If the response returns terminate, send a exit message to main and break the loop
        if response == "terminate":
            socket.send_string("Microservice A shutting down.")
            break

        # Send the processed respnse back to main program
        socket.send_string(response)

main()
