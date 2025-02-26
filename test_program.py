import zmq
import requests
import json

# Print all spell data
def print_data(spell_data):
    for spell in spell_data: 
        print(json.dumps(spell, indent=4))

# Print only name, level, classes
def print_name(spell_data):
    print()
    for spell in spell_data:
        name = spell["name"]
        level = spell["level"]
        class_names = [spell_class["name"] for spell_class in spell["classes"]]

        class_list = ", ".join(class_names)
            
        print(f"{name}: Level {level}, ({class_list})")

# Get input for sorting method
def get_input():
    print("\nHow would you like the spells to be sorted?")
    print("1. Sort by Name (Alphabetically)")
    print("2. Sort by level (Ascending or Descending)")
    print("3. Sort by Class (Alphabetically)")
    print("4. Quit")
    try:
        choice = int(input("Your choice (1 - 4): "))  
        return choice
    except:
        print("Invalid input, try again")
        return -1

# Get input for printing method
def get_print_method():
    print("How would you like to view the spells?")
    print("1. See all spell data (Json Object).")
    print("2. Name, Level, and Class only")
    try:
        choice = int(input("Your choice: "))  
        return choice
    except:
        print("Invalid input, try again")
        return -1

# Get input for either ascending or descending level sorting
def level_order():
    try:
        choice = int(input("Ascending or Descending? (1 or 2): "))
        if choice == 1:
            return False
        elif choice == 2:
            return True
    
    except:
        print("Invalid input, try again")
        return -1
    
# Get desired class name, input is not case sensitive
def get_class_name():
    class_name = input("Enter a class name: ").strip()
    return class_name

# main function
def main():
    # Create ZMQ context and socket
    context = zmq.Context() 
    socket = context.socket(zmq.REQ)

    # Bind socket to local host
    socket.connect("tcp://localhost:5555")

    choice = -1 # store users choice
    print_method = -1 # store print method

    while True:
        choice = get_input()

        if choice == 4:
            # Create termination message
            message = json.dumps({"end_program": True})
            print("Sending signal to microservice to end program")

            # Send message to microservice
            socket.send_string(message)

            # Recieve message and print confirmation from the microservice
            print(f"{socket.recv_string()}") 
            print("Bye!")
            break
 
        # ask user if they would like to sort their bookmarked spells
        use_bookmarks = int(input("Would you like to sort bookmarked spells? 1 or 2: ")) # 1 is yes and 2 is no
        spell_list = []
        if use_bookmarks == 1:
            spell_list = bookmarked_spells(sample_spells) # grab bookmarked spells
            bookmarks = True
        else:
            bookmarks = False


        if choice == 1:
            message = json.dumps({
                "sort_by": "name",
                "descending": None,
                "class_name": None,
                "bookmarks": bookmarks,
                "spell_list": spell_list
            })
            print(f"\nSending message: {message}\n")
            socket.send_string(message) # Send request to microservice
            result = socket.recv_string() # Recieve response from microservice
            print_method = get_print_method() # Ask user for printing method 

            try:
                spell_data = json.loads(result) # Parse Json response
                
                # Print based on user input
                if print_method == 1:
                    print_data(spell_data)
                else:
                    print_name(spell_data)

            except json.JSONDecodeError:
                print("Error: could not decode server response")

        
        elif choice == 2:
            order = level_order()
            message = json.dumps({
                "sort_by": "level",
                "descending": order,
                "class_name": None,
                "bookmarks": use_bookmarks,
                "spell_list": spell_list
            })
            print(f"\nSending message: {message}\n")
            socket.send_string(message) # Send request to microservice
            result = socket.recv_string() # Recieve response from microservice
            print_method = get_print_method() # Ask user for printing method 

            try:
                spell_data = json.loads(result) 

                if print_method == 1:
                    print_data(spell_data)
                else:
                    print_name(spell_data)

            except json.JSONDecodeError:
                print("Error: could not decode server response")

        elif choice == 3:
            message = json.dumps({
                "sort_by": "class",
                "descending": None,
                "class_name": get_class_name(),
                "bookmarks": use_bookmarks,
                "spell_list": spell_list
            })

            print(f"\nSending message: {message}\n")
            socket.send_string(message)
            result = socket.recv_string()

            try:
                spell_data = json.loads(result)

                # if no spells were returned, class name was invalid
                if spell_data == []:
                    print("Class not found.")
                    continue
                
                print_method = get_print_method()
                if print_method == 1:
                    print_data(spell_data)
                else:
                    print_name(spell_data)
            except json.JSONDecodeError:
                print("Error: could not decode server response")

        else:
            print("Invalid Input. Try again.")

# Function to grab a sample list of spells for testing purposes
def bookmarked_spells(sample_spells):
    base_url = "https://www.dnd5eapi.co/api/2014/spells/"
    spells = []

    for spell in sample_spells:
        url = base_url + spell
        response = requests.get(url)
        if response.status_code == 200:
            spells.append(response.json()) 
        else:
            print(f"Error: Could not fetch spell {spell} (Status Code {response.status_code})")
    
    return spells
        
#sample bookmarked spells
sample_spells = ["fear", "animate-dead", "guiding-bolt", "eyebite"]

if __name__ == "__main__":
    main()