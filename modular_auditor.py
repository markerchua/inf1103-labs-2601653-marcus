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

    if(quantity.lower() == "quit"):
            print("Final Report:")
            print("Total Units Processed: "+str(inventory))
            print("Total Rejected/Failed Entries: "+str(rejected))
            break