#A store manager needs to process a stream of daily deliveries. Staff often make errors
#(entering text instead of numbers, negative values, or exceeding storage capacity).
#Your job is to build the software that audits these entries in real-time.
#The inventory is saved to a file so it persists between runs.

INVENTORY_FILE = "inventory.txt"


# 1. Persistence: load the previously saved total and transaction history.
# If the file does not exist (e.g. first run), start with an empty inventory.
# File format - line 1: final total, line 2: transaction history separated by commas
def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as file:
            lines = file.read().splitlines()
        total = int(lines[0])
        history = []
        if len(lines) > 1 and lines[1] != "":
            for amount in lines[1].split(","):
                history.append(int(amount))
        print("Loaded saved inventory: " + str(total) + " units.")
        return total, history
    except FileNotFoundError:
        print("No saved inventory found. Starting with an empty inventory.")
        return 0, []
    except (ValueError, IndexError):
        #File exists but is empty or does not contain valid numbers
        print("Saved inventory file is invalid. Starting with an empty inventory.")
        return 0, []


# 2. Write-Back: save the final total and transaction history to the file
def save_inventory(total, history):
    history_text = ""
    for amount in history:
        if history_text != "":
            history_text += ","
        history_text += str(amount)
    with open(INVENTORY_FILE, "w") as file:
        file.write(str(total) + "\n")
        file.write(history_text + "\n")
    print("Inventory saved to " + INVENTORY_FILE)


# 3. Input validation
def get_valid_input():
    quantity = input(
        "Please enter a stock quantity or type 'quit' to get your final report: "
    )

    if quantity.lower() == "quit":
        return "quit"

    #quantity.isdigit() checks for negative numbers as "-" is not a digit and checks for text
    if quantity.isdigit():
        return int(quantity)

    return "invalid"


# 4. Total calculation
def process_delivery(current_total, new_value):
    return current_total + new_value


# 5. Tax calculation (10%)
def calculate_tax(amount):
    return amount * 0.10


# 6. Final report
def generate_report(total_units, failed_attempts, total_deliveries, taxes, history):
    print("Final Report:")
    print("Total Deliveries Processed: " + str(total_deliveries))
    print("Total Units Processed: " + str(total_units))
    print("Total Rejected/Failed Entries: " + str(failed_attempts))
    print("Total Tax: " + str(taxes))
    print("Transaction History: " + str(history))


print("=======================")
print("Smart Inventory Auditor")
print("=======================")
inventory, history = load_inventory() #History Tracking: history stores every valid transaction amount
rejected = 0
deliveries = 0
taxes = 0

while (True):

    result = get_valid_input()

    if result == "quit":
        save_inventory(inventory, history)
        generate_report(inventory, rejected, deliveries, taxes, history)
        break
    elif result == "invalid":
        rejected = rejected + 1
        print("Please give the correct input! We only accept positive digits.")
    elif process_delivery(inventory, result) > 500:
        print("Warning! Inventory exceeded 500 units. Please try again.")
        break
    else:
        inventory = process_delivery(inventory, result)
        history.append(result)
        taxes += calculate_tax(result)
        deliveries = deliveries + 1
        print("You currently have " + str(inventory) + " units in your inventory.")
