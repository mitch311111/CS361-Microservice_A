import zmq
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

    choice = -1
    print_method = -1

    while True:
        choice = get_input()
        if choice == 1:
            message = json.dumps({
                "sort_by": "name",
                "descending": None,
                "class_name": None
            })
            print(f"\nSending message: {message}\n")
            socket.send_string(message)
            result = socket.recv_string()
            print_method = get_print_method()

            try:
                spell_data = json.loads(result)
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
                "class_name": None
            })
            print(f"\nSending message: {message}\n")
            socket.send_string(message)
            result = socket.recv_string()
            print_method = get_print_method()

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
                "class_name": get_class_name()
            })

            print(f"\nSending message: {message}\n")
            socket.send_string(message)
            result = socket.recv_string()

            try:
                spell_data = json.loads(result)
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

        elif choice == 4:
            message = json.dumps({"end_program": True})
            print("Sending signal to microservice to end program")
            socket.send_string(message)
            print(f"{socket.recv_string()}") 
            print("Bye!")
            break

        else:
            print("Invalid Input. Try again.")
    

main()