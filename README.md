# Spell Sorting Microservice
This microservice fetches a list of spells from the DND5eAPI and returns them in a sorted list. The methods of sorting include...
- Sorting by Spell Name (Alphabetically)
- Sorting by Level (Ascending or Descending)
- Sorting by Class (Alphabetically)

## Prerequisites
This microservice A has been written in Python so a compatible version of Python must be installed on your machine. The microservice uses the ZeroMQ pipeline to send/receive data between this microservice and 
another program. To start the microservice and begin listening, you must run the following command:
```
python microservice.py
```

## How to REQUEST Data
To send and receive messages from the microservice, you will need to import the **```zmq```** and **```json```** packages.

### Request Format
The request is sent as a JSON-encoded string. Each request must contain the following fields:
- ```sort_by```: Defines the sorting/filtering criteria. Can be one of the following:
  - ```"name"``` for sorting by name
  - ```"level"``` for sorting by level.
  - ```"class"``` for sorting by class.
- ```descending``` (optional): A boolean value that specifies if the data should be sorted in descending order. Relevant for sorting by level only.
- ```class_name``` (optional): The name of the class to filter by, used only for sorting by classes. This should be a valid D&D class name (e.g., "Cleric", "Wizard", etc.)

### Example requests

**Sort by Name (Alphabetically):**
```
{
    "sort_by": "name",
    "descending": None,
    "class_name": None
}
```
**Sort by level (Ascending):**
```
{
    "sort_by": "level",
    "descending": false,
    "class_name": None
}
```
**Sort by level (Descending):**
```
{
    "sort_by": "level",
    "descending": true,
    "class_name": None
}
```
**Sort by class (For Example, "Wizard"):**
```
{
    "sort_by": "class",
    "descending": None,
    "class_name": "Wizard"
}
```

### Example Call
To send a request, you will need to communicate with the microservice using a ZeroMQ socket on ```localhost:5555```. The client should send a message in the JSON format to the microservice.

Here's an example snippet for sending a request:
```
import zmq
import json

# create ZMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # connect to the microservice

# prepare your request (JSON formatted message)
message = json.dumps({
    "sort_by": "name",
    "descending": None,
    "class_name": None
})

# send the message
socket.send_string(message)
```
If you wish to terminate the microservice, you can send a request with the following JSON format:
```
{
"end_program: true
}
```

The microservice will respond with a termination message and shut down gracefully.
Example snippet: 
```
message = json.dumps({end_program: True})
socket.send_string(message)
```

## How to RECEIVE Data
When the client sends a request message to the microservice, it will receive a response with the requested spell data in JSON format.
The microservice processes the request and returns the sorted list of spell data based on the parameters given by the client.

###Example Call
```
socket.send_string(message)
result = socket.recv_string()

# convert the JSON-encoded string (result) into a Python dictionary
data = json.loads(result)
```
# UML Sequence Diagram
![UML Diagram for Jamies Microservice A - Spell Sorting](https://github.com/mitch311111/CS361-Microservice_A/blob/main/UMLDiagram.png)
