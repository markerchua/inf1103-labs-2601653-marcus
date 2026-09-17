print("=======================")
print("Smart Inventory Auditor")
print("=======================")
inventory = 0
rejected = 0
deliveries = 0
taxes = 0


def get_valid_input():
    quantity = input(
        "Please enter a stock quantity or type 'quit' to get your final report: "
    )

    if quantity.lower() == "quit":
        return "quit"

    if quantity.isdigit():
        return int(quantity)

    return "invalid"


# 2. Total calculation
def process_delivery(current_total, new_value):
    return current_total + new_value


# 3. Tax calculation (10%)
def calculate_tax(amount):
    return amount * 0.10

def generate_report(total_units, failed_attempts, total_deliveries,taxes):
    print("Final Report:")
    print("Total Deliveries Processed: " + str(total_deliveries))
    print("Total Units Processed: " + str(total_units))
    print("Total Rejected/Failed Entries: " + str(failed_attempts))
    print("Total Tax: "+str(taxes))

while (True):
    
    result = get_valid_input()

    if result == "quit":
        generate_report(inventory, rejected, deliveries,taxes)
        break
    elif result == "invalid":
        rejected = rejected + 1
        print("Please give the correct input! We only accept positive digits.")
    else:
        inventory = process_delivery(inventory, result)
        tax = calculate_tax(result)
        taxes += tax
        deliveries = deliveries + 1
        if inventory > 500:
            print("Warning! Inventory exceeded 500 units. Please try again.")
            break
        else:
            print("You currently have "+ str(inventory)+ " units in your inventory.")
    