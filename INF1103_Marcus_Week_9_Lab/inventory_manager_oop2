#The store manager is happy with the Week 5 inventory system, but it has been refactored
#using Object-Oriented Programming. Products are now Product objects managed by an
#Inventory object, instead of dictionaries in a list.
#Lab 7 extends it with inheritance: every product is either a PhysicalProduct or a
#DigitalProduct, and physical products can be shipped (CanBeShipped interface).
#
#Responsibilities (Single Responsibility Principle):
#  Product       - abstract class, stores product information and manages its own state
#  PhysicalProduct / DigitalProduct - add their own attributes and behaviour
#  CanBeShipped  - interface for anything that can calculate a shipping cost
#  Inventory     - stores, adds, searches and displays products
#  File Handling - load_inventory() and save_inventory() load/save inventory.json
#  Main Program  - displays the menu, gets user input and calls Inventory methods

import io
import json
import os
import sys
import tempfile
from abc import ABC, abstractmethod
from contextlib import redirect_stdout

#inventory.json is kept in the same folder as this script, so it is found
#no matter which folder the program is run from
INVENTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


#Product class
#SRP: the Product class has one responsibility - represent and manage a single product.
#It does NOT load/save files, ask the user for input, show the menu or manage the inventory.
#Abstract class: Product inherits from ABC and has an abstract method, so a generic
#Product can never be created directly - every product must be a PhysicalProduct or
#a DigitalProduct.
class Product(ABC):

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

    #Abstract method: no implementation here. Every subclass must provide its own
    #get_fulfilment_info() explaining how that type of product reaches the customer.
    @abstractmethod
    def get_fulfilment_info(self):
        pass


#CanBeShipped interface
#Python has no interface keyword, so an abstract base class is used as an
#interface-style contract. This is a 'must be able to' relationship, not 'is-a':
#any class that implements CanBeShipped must be able to calculate its shipping cost.
#It has no attributes or shipping details, so any shippable object can sign the contract.
class CanBeShipped(ABC):

    #Implementing classes must provide a way to calculate shipping costs
    @abstractmethod
    def calculate_shipping_cost(self):
        pass


#PhysicalProduct class
#Inheritance: a PhysicalProduct 'is-a' Product, so it inherits all of Product's
#attributes and methods, and adds what is unique to a physical item - its weight.
#Interface: a PhysicalProduct also 'must be able to' be shipped, so it implements
#CanBeShipped. This is still single class inheritance - Product is its only parent
#class, and CanBeShipped is an interface (contract), not a second parent class.
class PhysicalProduct(Product, CanBeShipped):

    #Shipping rule: a base fee plus a charge for every kilogram
    BASE_SHIPPING_FEE = 5.00   #$ per parcel
    SHIPPING_RATE_PER_KG = 2.00   #$ per kg

    #Reuse the Product constructor with super() to set up the ID, name, price and stock,
    #then initialise the extra weight attribute
    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        self.__weight = float(weight)   #float, in kilograms

    def get_weight(self):
        return self.__weight

    #Method overriding: replaces Product's display_information() for physical products.
    #super() lets the parent display the common product information, then the child
    #only adds the part that is unique to it - the weight.
    def display_information(self):
        super().display_information()
        print("      Weight: " + format(self.__weight, ".2f") + " kg")

    #Implements Product's abstract method: physical products are shipped
    def get_fulfilment_info(self):
        return self.get_name() + " requires physical shipping to the customer."

    #Implements CanBeShipped's abstract method: shipping is based on the product's weight
    def calculate_shipping_cost(self):
        return self.BASE_SHIPPING_FEE + self.__weight * self.SHIPPING_RATE_PER_KG


#DigitalProduct class
#Inheritance: a DigitalProduct 'is-a' Product, so it inherits all of Product's
#attributes and methods. It has no weight, but adds a download size instead.
class DigitalProduct(Product):

    #Reuse the Product constructor with super() to set up the ID, name, price and stock,
    #then initialise the extra download_size attribute
    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self.__download_size = float(download_size)   #float, in megabytes

    def get_download_size(self):
        return self.__download_size

    #Method overriding: replaces Product's display_information() for digital products.
    #super() lets the parent display the common product information, then the child
    #only adds the part that is unique to it - the download size.
    def display_information(self):
        super().display_information()
        print("      Download Size: " + format(self.__download_size, ".2f") + " MB")

    #Implements Product's abstract method: digital products are delivered digitally
    def get_fulfilment_info(self):
        return self.get_name() + " is delivered digitally via a download link."


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


# File Handling: load inventory.json if it exists and use each saved product's
# "type" to create the right subclass (PhysicalProduct or DigitalProduct).
# Otherwise, begin with an empty inventory.
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
            #Products saved before Lab 7 have no "type" - they were all physical items,
            #so they load as physical products with an unknown (0 kg) weight
            product_type = item.get("type", "physical")
            if product_type == "physical":
                product = PhysicalProduct(item["id"], item["name"], item["price"], item["stock"], item.get("weight", 0))
            elif product_type == "digital":
                product = DigitalProduct(item["id"], item["name"], item["price"], item["stock"], item["download_size"])
            else:
                raise ValueError("Unknown product type: " + str(product_type))
            inventory.add_product(product)
        print("Inventory loaded successfully.")
        return inventory
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        #File exists but does not contain valid product data
        print("inventory.json is invalid. Starting with an empty inventory.")
        return Inventory()


# File Handling: save every Product in the Inventory to inventory.json.
# JSON cannot store objects directly, so each Product is turned back into a
# dictionary using its getters, with a "type" identifier and the extra
# attribute for that type, so the right subclass can be created when loading.
# Returns True if saved, False if the file could not be written.
def save_inventory(inventory):
    items = []
    for product in inventory.get_products():
        item = {
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
        }
        if isinstance(product, PhysicalProduct):
            item["type"] = "physical"
            item["weight"] = product.get_weight()
        elif isinstance(product, DigitalProduct):
            item["type"] = "digital"
            item["download_size"] = product.get_download_size()
        items.append(item)
    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(items, file, indent=4)
        return True
    except OSError:
        print("Error! Could not save inventory to inventory.json.")
        return False


# Main Program helpers: getting user input is the main program's job, not the classes'

# Keep asking until the user enters a number that is not negative
# (used for price, weight and download size)
def get_valid_number(prompt):
    while True:
        try:
            number = float(input(prompt))
            if number >= 0:
                return number
        except ValueError:
            pass
        print("Invalid number! Please enter a positive number.")


# Keep asking until the user enters a whole number that is not negative
#isdigit() rejects text and negative numbers as "-" is not a digit
def get_valid_stock(prompt):
    while True:
        stock = input(prompt)
        if stock.isdigit():
            return int(stock)
        print("Invalid quantity! We only accept positive whole numbers.")


# Keep asking until the user chooses a product type: 1 = physical, 2 = digital
def get_product_type():
    print("Product Type:")
    print("1. Physical Product")
    print("2. Digital Product")
    while True:
        choice = input("Enter product type: ").strip()
        if choice == "1":
            return "physical"
        if choice == "2":
            return "digital"
        print("Invalid choice! Please enter 1 or 2.")


# Menu option 2: ask for the product type and details, create a PhysicalProduct
# or DigitalProduct object and pass it to the Inventory
def add_product_menu(inventory):
    print("Add New Product")
    product_type = get_product_type()
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

    price = get_valid_number("Price: ")
    stock = get_valid_stock("Stock Quantity: ")

    #Ask for the extra attribute that belongs to the chosen product type
    if product_type == "physical":
        weight = get_valid_number("Weight (kg): ")
        product = PhysicalProduct(product_id, name, price, stock, weight)
    else:
        download_size = get_valid_number("Download Size (MB): ")
        product = DigitalProduct(product_id, name, price, stock, download_size)

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


# Menu option 4: ask the Inventory to find the Product, then let the product show
# its own details. Each product type displays its own information and fulfilment.
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
    product.display_information()
    print("Fulfilment: " + product.get_fulfilment_info())
    #Only products that implement CanBeShipped have a shipping cost
    if isinstance(product, CanBeShipped):
        print("Shipping Cost: $" + format(product.calculate_shipping_cost(), ".2f"))
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


# 7. Testing and review: automatic tests for every item in the Lab 7 checklist.
# Run with:  python inventory_manager_oop2.py test
# The tests use their own temporary JSON file, so the real inventory.json is never changed.

# Print one PASS/FAIL line and return whether the check passed
def check(description, passed):
    print("  " + ("PASS" if passed else "FAIL") + " - " + description)
    return passed


# Capture everything a product's display_information() prints, so it can be checked
def get_display_output(product):
    captured = io.StringIO()
    with redirect_stdout(captured):
        product.display_information()
    return captured.getvalue()


def run_tests():
    results = []
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 8, 3.5)
    operating_system = DigitalProduct("P006", "Operating System", 139.99, 100, 4500)

    # 1. Physical products store and display their weights
    print("1. Physical products store and display their weights")
    guitar.display_information()
    output = get_display_output(guitar)
    results.append(check("weight is stored (3.5 kg)", guitar.get_weight() == 3.5))
    results.append(check("common info comes from Product", "ID: P005 | Name: Guitar | Price: $350.00 | Stock: 8" in output))
    results.append(check("weight is displayed", "Weight: 3.50 kg" in output))
    print()

    # 2. Digital products store and display their download sizes
    print("2. Digital products store and display their download sizes")
    operating_system.display_information()
    output = get_display_output(operating_system)
    results.append(check("download size is stored (4500 MB)", operating_system.get_download_size() == 4500))
    results.append(check("common info comes from Product", "ID: P006 | Name: Operating System | Price: $139.99 | Stock: 100" in output))
    results.append(check("download size is displayed", "Download Size: 4500.00 MB" in output))
    print()

    # 3. Both subclasses implement get_fulfilment_info()
    print("3. Both subclasses implement get_fulfilment_info()")
    print("  " + guitar.get_fulfilment_info())
    print("  " + operating_system.get_fulfilment_info())
    results.append(check("PhysicalProduct requires physical shipping", "physical shipping" in guitar.get_fulfilment_info()))
    results.append(check("DigitalProduct is delivered digitally", "delivered digitally" in operating_system.get_fulfilment_info()))
    print()

    # 4. The abstract Product class cannot be instantiated directly
    print("4. The abstract Product class cannot be instantiated directly")
    try:
        Product("P001", "Laptop", 1200.00, 15)
        results.append(check("Product cannot be created", False))
    except TypeError as error:
        print("  TypeError: " + str(error))
        results.append(check("Product cannot be created", True))
    print()

    # 5. Physical products can calculate shipping costs ($5.00 base fee + $2.00 per kg)
    print("5. Physical products can calculate shipping costs")
    shipping_tests = [
        (PhysicalProduct("P007", "Headphones", 89.00, 20, 0.5), 6.00),
        (guitar, 12.00),
        (PhysicalProduct("P008", "Amplifier", 499.00, 4, 20), 45.00),
    ]
    for product, expected_cost in shipping_tests:
        cost = product.calculate_shipping_cost()
        description = product.get_name() + " (" + format(product.get_weight(), ".2f") + " kg) costs $" + format(cost, ".2f") + " to ship"
        results.append(check(description, abs(cost - expected_cost) < 0.001))
    results.append(check("PhysicalProduct implements CanBeShipped", isinstance(guitar, CanBeShipped)))
    print()

    # 6. Digital products are not required to implement shipping behaviour
    print("6. Digital products are not required to implement shipping behaviour")
    results.append(check("DigitalProduct does not implement CanBeShipped", not isinstance(operating_system, CanBeShipped)))
    results.append(check("DigitalProduct has no calculate_shipping_cost()", not hasattr(operating_system, "calculate_shipping_cost")))
    results.append(check("DigitalProduct can still be created", isinstance(operating_system, Product)))
    print()

    # 7. Inventory operations continue to work
    print("7. Inventory operations continue to work")
    inventory = Inventory()
    results.append(check("add a physical product", inventory.add_product(guitar)))
    results.append(check("add a digital product", inventory.add_product(operating_system)))
    results.append(check("duplicate product ID is rejected", not inventory.add_product(PhysicalProduct("p005", "Other", 1, 1, 1))))
    results.append(check("search finds a product (not case-sensitive)", inventory.search_product("p006") is operating_system))
    results.append(check("search returns None for an unknown ID", inventory.search_product("P999") is None))
    results.append(check("update stock to 50", guitar.update_stock(50) and guitar.get_stock() == 50))
    results.append(check("negative stock is rejected", not guitar.update_stock(-5) and guitar.get_stock() == 50))
    captured = io.StringIO()
    with redirect_stdout(captured):
        inventory.display_all()
    output = captured.getvalue()
    results.append(check("display all shows both products with their extra info", "Weight: 3.50 kg" in output and "Download Size: 4500.00 MB" in output))
    print()

    # 8. JSON saving and loading preserve the correct product types
    print("8. JSON saving and loading preserve the correct product types")
    global INVENTORY_FILE
    real_file = INVENTORY_FILE
    INVENTORY_FILE = os.path.join(tempfile.mkdtemp(), "test_inventory.json")
    try:
        save_inventory(inventory)
        with open(INVENTORY_FILE, "r") as file:
            saved = json.load(file)
        results.append(check("saved file has a \"type\" for each product", [item["type"] for item in saved] == ["physical", "digital"]))
        results.append(check("saved file has weight and download_size", saved[0]["weight"] == 3.5 and saved[1]["download_size"] == 4500))

        with redirect_stdout(io.StringIO()):
            loaded = load_inventory()
        loaded_guitar = loaded.search_product("P005")
        loaded_os = loaded.search_product("P006")
        results.append(check("Guitar is loaded back as a PhysicalProduct", type(loaded_guitar) == PhysicalProduct))
        results.append(check("Operating System is loaded back as a DigitalProduct", type(loaded_os) == DigitalProduct))
        results.append(check("weight and updated stock are restored", loaded_guitar.get_weight() == 3.5 and loaded_guitar.get_stock() == 50))
        results.append(check("download size is restored", loaded_os.get_download_size() == 4500))
    finally:
        os.remove(INVENTORY_FILE)
        os.rmdir(os.path.dirname(INVENTORY_FILE))
        INVENTORY_FILE = real_file
    print()

    passed = results.count(True)
    print(str(passed) + " of " + str(len(results)) + " tests passed.")
    print("All tests passed!" if passed == len(results) else "Some tests FAILED.")


# Main Program
#Running "python inventory_manager_oop2.py test" runs the tests instead of the menu
if len(sys.argv) > 1 and sys.argv[1] == "test":
    run_tests()
    sys.exit()

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
