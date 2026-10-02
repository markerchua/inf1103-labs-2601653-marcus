#The store manager needs a system that remembers inventory levels even after the
#program closes. Furthermore, they need to store a history of all transaction amounts,
#not just the running total.

import json
import os

# 1. Data Representation: each inventory item is a dictionary,
# and all the products are stored together in a list, e.g.
# [{"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15}, ...]
# The list is loaded from and saved to inventory.json.

#inventory.json is kept in the same folder as this script, so it is found
#no matter which folder the program is run from
INVENTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


# 3. Data Persistence: load the inventory list from inventory.json if it exists.
# Otherwise, begin with an empty inventory.
def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        print("inventory.json not found.")
        print("Starting with an empty inventory.")
        return []

    print("inventory.json found.")
    try:
        with open(INVENTORY_FILE, "r") as file:
            items = json.load(file)
        print("Inventory loaded successfully.")
        return items
    except json.JSONDecodeError:
        #File exists but does not contain valid JSON
        print("inventory.json is invalid. Starting with an empty inventory.")
        return []


# Save the inventory list to inventory.json.
# Returns True if saved, False if the file could not be written.
def save_inventory(items):
    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(items, file, indent=4)
        return True
    except OSError:
        print("Error! Could not save inventory to inventory.json.")
        return False


# Helper: find a product dictionary by its ID (not case-sensitive), or None if not found
def find_product(items, product_id):
    for item in items:
        if item["id"].upper() == product_id.upper():
            return item
    return None


# Helper: keep asking until the user enters a price that is a number and not negative
def get_valid_price(prompt):
    while True:
        try:
            price = float(input(prompt))
            if price >= 0:
                return price
        except ValueError:
            pass
        print("Invalid price! Please enter a positive number.")


# Helper: keep asking until the user enters a whole number that is not negative
#isdigit() rejects text and negative numbers as "-" is not a digit
def get_valid_stock(prompt):
    while True:
        stock = input(prompt)
        if stock.isdigit():
            return int(stock)
        print("Invalid quantity! We only accept positive whole numbers.")


# 2. Data Manipulation
def display_all(items):
    print("Current Inventory")
    print("-" * 45)
    if len(items) == 0:
        print("No products in inventory.")
    for item in items:
        print("ID: " + item["id"] + " | Name: " + item["name"] + " | Price: $" + format(item["price"], ".2f") + " | Stock: " + str(item["stock"]))
    print("-" * 45)


def add_product(items):
    print("Add New Product")
    product_id = input("Product ID: ").strip().upper()
    if product_id == "":
        print("Product ID cannot be empty.")
        return
    if find_product(items, product_id) is not None:
        print("Product ID " + product_id + " already exists.")
        return

    name = input("Product Name: ").strip()
    if name == "":
        print("Product name cannot be empty.")
        return

    price = get_valid_price("Price: ")
    stock = get_valid_stock("Stock Quantity: ")

    items.append({"id": product_id, "name": name, "price": price, "stock": stock})
    print()
    print("Product added successfully!")


def update_stock(items):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip()
    print()
    item = find_product(items, product_id)
    if item is None:
        print("Product not found.")
        return

    print("Product Found:")
    print("Name: " + item["name"])
    print("Current Stock: " + str(item["stock"]))
    print()
    item["stock"] = get_valid_stock("New Stock Quantity: ")
    print()
    print("Stock updated successfully!")


def search_product(items):
    print("Search Product")
    product_id = input("Enter Product ID: ").strip()
    print()
    item = find_product(items, product_id)
    if item is None:
        print("Product not found.")
        return

    print("Product Found")
    print("-" * 45)
    print("ID: " + item["id"])
    print("Name: " + item["name"])
    print("Price: $" + format(item["price"], ".2f"))
    print("Stock: " + str(item["stock"]))
    print("-" * 45)


def display_menu():
    print()
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


print("=" * 40)
print("INVENTORY MANAGEMENT SYSTEM")
print("=" * 40)
print()
inventory = load_inventory()

while True:
    display_menu()
    print()
    option = input("Enter option: ").strip()
    print()

    if option == "1":
        display_all(inventory)
    elif option == "2":
        add_product(inventory)
    elif option == "3":
        update_stock(inventory)
    elif option == "4":
        search_product(inventory)
    elif option == "5":
        print("Saving inventory...")
        if save_inventory(inventory):
            print("Inventory saved successfully to inventory.json.")
    elif option == "6":
        #Save automatically before exiting so no changes are lost
        print("Saving inventory before exit...")
        if save_inventory(inventory):
            print("Inventory saved successfully.")
        print()
        print("Thank you for using Inventory Management System.")
        print("Program terminated.")
        break
    else:
        print("Invalid option! Please choose from the menu.")
