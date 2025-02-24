import zmq
import json

def print_data(spell_data):
    for spell in spell_data: 
        print(json.dumps(spell, indent=4))

def print_name(spell_data):
    for spell in spell_data:
        name = spell["name"]
        level = spell["level"]
        class_names = [spell_class["name"] for spell_class in spell["classes"]]

        class_list = ", ".join(class_names)
            
        print(f"{name}: Level {level}, ({class_list})")

def get_input():
    print("1. Sort by name (Alphabetically)\n")
    print("2. Sort by level (Ascending or Descending)\n")
    print("3. Sort by Class (Alphabetically)\n")
    print("4. quit")
    try:
        choice = int(input("Your choice: "))  
        return choice
    except:
        print("Invalid input, try again")
        return -1

def get_print_method():
    print("How would you like to view the spells?")
    print("1. See all spell data.")
    print("2. Name only")
    try:
        choice = int(input("Your choice: "))  
        return choice
    except:
        print("Invalid input, try again")
        return -1

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
    

def get_class_name():
    class_name = input("Enter a class name: ").strip()
    return class_name

def main():
    context = zmq.Context() 

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    choice = -1
    print_method = -1

    # spell_data = load_spells()

    while True:
        choice = get_input()
        if choice == 1:
            message = json.dumps({
                "sort_by": "name",
                "descending": None,
                "class_name": None
            })
            print(f"Sending message: {message}")
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
            print(f"Sending message: {message}")
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

        if choice == 3:
            message = json.dumps({
                "sort_by": "class",
                "descending": None,
                "class_name": get_class_name()
            })

            print(f"Sending message: {message}")
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

        if choice == 4:
            break
    

main()