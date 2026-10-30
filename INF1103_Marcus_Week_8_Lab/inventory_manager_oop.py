#The store manager is happy with the Week 5 inventory system, but it has been refactored
#using Object-Oriented Programming. Products are now Product objects managed by an
#Inventory object, instead of dictionaries in a list.
#
#Responsibilities (Single Responsibility Principle):
#  Product       - stores product information and manages its own state
#  Inventory     - stores, adds, searches and displays products
#  File Handling - load_inventory() and save_inventory() load/save inventory.json
#  Main Program  - displays the menu, gets user input and calls Inventory methods

import json
import os

#inventory.json is kept in the same folder as this script, so it is found
#no matter which folder the program is run from
INVENTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


#Product class
#SRP: the Product class has one responsibility - represent and manage a single product.
#It does NOT load/save files, ask the user for input, show the menu or manage the inventory.
class Product:

    #Initializer (constructor): the parameters are the values passed in from outside,
    #the self.__ attributes belong to this object. The double underscore marks them as
    #private, so outside code should use the public methods below instead.
    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id  #String
        self.__name = name              #String
        self.__price = float(price)     #float
        self.__stock = int(stock)       #int

    #Gett
    # ers: let other code read the attributes without being able to change them
    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    #Encapsulation: the stock can only be changed through this method, so the Product
    #decides whether the new value is allowed before assigning it to self.__stock.
    #Returns True if the stock was updated, False if the quantity was rejected.
    def update_stock(self, quantity):
        if type(quantity) != int or quantity < 0:
            return False
        self.__stock = quantity
        return True

    #Display this product's information on one line
    def display_information(self):
        print("ID: " + self.__product_id + " | Name: " + self.__name + " | Price: $" + format(self.__price, ".2f") + " | Stock: " + str(self.__stock))


#Inventory class
#SRP: the Inventory class has one responsibility - manage a collection of Product objects.
#It does NOT load/save files, ask the user for input or show the menu.
class Inventory:

    #Start with an empty list that will hold Product objects
    def __init__(self):
        self.__products = []  #list of Product

    #Add a Product object to the inventory.
    #Returns True if added, False if a product with the same ID already exists.
    def add_product(self, product):
        if self.search_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    #Find a product by its ID (not case-sensitive).
    #Returns the Product object, or None if not found.
    def search_product(self, product_id):
        for product in self.__products:
            if product.get_product_id().upper() == product_id.upper():
                return product
        return None

    #Display every product in the inventory
    def display_all(self):
        print("Current Inventory")
        print("-" * 45)
        if len(self.__products) == 0:
            print("No products in inventory.")
        for product in self.__products:
            product.display_information()
        print("-" * 45)

    #Return a copy of the product list (e.g. for saving), so outside code
    #cannot add or remove products without going through add_product()
    def get_products(self):
        return list(self.__products)


# File Handling: load inventory.json if it exists and turn each saved product
# into a Product object. Otherwise, begin with an empty inventory.
# Returns an Inventory object.
def load_inventory():
    inventory = Inventory()
    if not os.path.exists(INVENTORY_FILE):
        print("inventory.json not found.")
        print("Starting with an empty inventory.")
        return inventory

    print("inventory.json found.")
    try:
        with open(INVENTORY_FILE, "r") as file:
            items = json.load(file)
        for item in items:
            product = Product(item["id"], item["name"], item["price"], item["stock"])
            inventory.add_product(product)
        print("Inventory loaded successfully.")
        return inventory
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        #File exists but does not contain valid product data
        print("inventory.json is invalid. Starting with an empty inventory.")
        return Inventory()


# File Handling: save every Product in the Inventory to inventory.json.
# JSON cannot store objects directly, so each Product is turned back into a
# dictionary using its getters.
# Returns True if saved, False if the file could not be written.
def save_inventory(inventory):
    items = []
    for product in inventory.get_products():
        items.append({
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
        })
    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(items, file, indent=4)
        return True
    except OSError:
        print("Error! Could not save inventory to inventory.json.")
        return False


# Main Program helpers: getting user input is the main program's job, not the classes'

# Keep asking until the user enters a price that is a number and not negative
def get_valid_price(prompt):
    while True:
        try:
            price = float(input(prompt))
            if price >= 0:
                return price
        except ValueError:
            pass
        print("Invalid price! Please enter a positive number.")


# Keep asking until the user enters a whole number that is not negative
#isdigit() rejects text and negative numbers as "-" is not a digit
def get_valid_stock(prompt):
    while True:
        stock = input(prompt)
        if stock.isdigit():
            return int(stock)
        print("Invalid quantity! We only accept positive whole numbers.")


# Menu option 2: ask for the product details, create a Product object and
# pass it to the Inventory
def add_product_menu(inventory):
    print("Add New Product")
    product_id = input("Product ID: ").strip().upper()
    if product_id == "":
        print("Product ID cannot be empty.")
        return
    if inventory.search_product(product_id) is not None:
        print("Product ID " + product_id + " already exists.")
        return

    name = input("Product Name: ").strip()
    if name == "":
        print("Product name cannot be empty.")
        return

    price = get_valid_price("Price: ")
    stock = get_valid_stock("Stock Quantity: ")

    product = Product(product_id, name, price, stock)
    inventory.add_product(product)
    print()
    print("Product added successfully!")


# Menu option 3: find the Product and ask it to update its own stock
def update_stock_menu(inventory):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip()
    print()
    product = inventory.search_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    print("Name: " + product.get_name())
    print("Current Stock: " + str(product.get_stock()))
    print()
    new_stock = get_valid_stock("New Stock Quantity: ")
    print()
    if product.update_stock(new_stock):
        print("Stock updated successfully!")
    else:
        print("Stock could not be updated.")


# Menu option 4: ask the Inventory to find the Product and show its details
def search_product_menu(inventory):
    print("Search Product")
    product_id = input("Enter Product ID: ").strip()
    print()
    product = inventory.search_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found")
    print("-" * 45)
    print("ID: " + product.get_product_id())
    print("Name: " + product.get_name())
    print("Price: $" + format(product.get_price(), ".2f"))
    print("Stock: " + str(product.get_stock()))
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


# Main Program
print("=" * 40)
print("INVENTORY MANAGEMENT SYSTEM")
print("=" * 40)
print()
inventory = load_inventory()  #Inventory object holding Product objects

while True:
    display_menu()
    print()
    option = input("Enter option: ").strip()
    print()

    if option == "1":
        inventory.display_all()
    elif option == "2":
        add_product_menu(inventory)
    elif option == "3":
        update_stock_menu(inventory)
    elif option == "4":
        search_product_menu(inventory)
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
