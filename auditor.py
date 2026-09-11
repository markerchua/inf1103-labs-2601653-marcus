#A store manager needs to process a stream of daily deliveries. Staff often make errors
#(entering text instead of numbers, negative values, or exceeding storage capacity).
#Your job is to build the software that audits these entries in real-time.

print("=======================")
print("Smart Inventory Auditor")
print("=======================")
inventory = 0
rejected = 0

while (True):
    
    quantity =input("Please enter a stock quantity or type 'quit' to get your final report: ")


    #quantity.isdigit() checks for negative numbers as "-" is not a digit and checks for text
    if (quantity.isdigit()==False):
        print("Please give the correct input! We only accept positive digits.")
        rejected += 1

    else:
            if (int(quantity)+inventory>500):
                 print("Warning! Inventory exceeded 500 units. Please try again.")
                 break
            
            else:
                inventory = inventory + int(quantity)
                print("You currently have "+ str(inventory)+ " units in your inventory.")