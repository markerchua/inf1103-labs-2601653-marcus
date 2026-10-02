#The store manager needs a system that remembers inventory levels even after the
#program closes. Furthermore, they need to store a history of all transaction amounts,
#not just the running total.

# 1. Data Representation: each inventory item is a dictionary,
# and all the products are stored together in a list
inventory = [
    {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
    {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
    {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25},
]


def display_inventory(items):
    print("Current Inventory")
    print("-" * 45)
    for item in items:
        print("ID: " + item["id"] + " | Name: " + item["name"] + " | Price: $" + format(item["price"], ".2f") + " | Stock: " + str(item["stock"]))
    print("-" * 45)


print("=" * 40)
print("INVENTORY MANAGEMENT SYSTEM")
print("=" * 40)
print()
display_inventory(inventory)
