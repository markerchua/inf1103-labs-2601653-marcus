#A store manager needs to process a stream of daily deliveries. Staff often make errors
#(entering text instead of numbers, negative values, or exceeding storage capacity).
#Your job is to build the software that audits these entries in real-time.
#The inventory is saved to a file so it persists between runs.

INVENTORY_FILE = "inventory.txt"

print("=======================")
print("Smart Inventory Auditor")
print("=======================")
rejected = 0
history = [] #History Tracking: stores every valid transaction amount entered

#Persistence: load the previously saved inventory. If the file does not exist
#(e.g. first run), start with an empty inventory instead of crashing.
try:
    with open(INVENTORY_FILE, "r") as file:
        inventory = int(file.read().strip())
    print("Loaded saved inventory: " + str(inventory) + " units.")
except FileNotFoundError:
    inventory = 0
    print("No saved inventory found. Starting with an empty inventory.")
except ValueError:
    #File exists but does not contain a valid number
    inventory = 0
    print("Saved inventory file is invalid. Starting with an empty inventory.")

while (True):

    quantity = input("Please enter a stock quantity or type 'quit' to get your final report: ")

    #quantity.isdigit() checks for negative numbers as "-" is not a digit and checks for text
    if(quantity.lower() == "quit"):
        #Save the inventory so it can be loaded the next time the program starts
        with open(INVENTORY_FILE, "w") as file:
            file.write(str(inventory))
        print("Final Report:")
        print("Total Units Processed: "+str(inventory))
        print("Total Rejected/Failed Entries: "+str(rejected))
        print("Valid Transactions This Session: "+str(history))
        print("Inventory saved to " + INVENTORY_FILE)
        break

    elif (quantity.isdigit()==False):
        print("Please give the correct input! We only accept positive digits.")
        rejected += 1

    elif (int(quantity)+inventory>500):
        print("Warning! Inventory exceeded 500 units. Please try again.")
        break

    else:
        inventory = inventory + int(quantity)
        history.append(int(quantity))
        print("You currently have "+ str(inventory)+ " units in your inventory.")
