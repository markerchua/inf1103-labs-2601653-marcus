#The store manager is happy with the Week 5 inventory system, but it has been refactored
#using Object-Oriented Programming. Products are now Product objects managed by an
#Inventory object, instead of dictionaries in a list.
#Lab 7 extends it with inheritance: every product is either a PhysicalProduct or a
#DigitalProduct, and physical products can be shipped (CanBeShipped interface).
#Lab 8 models object relationships: Supplier (association), Inventory (aggregation)
#and Order/OrderLine (composition), with type hints that match the UML diagram.
#
#Responsibilities (Single Responsibility Principle) - one class per file:
#  Supplier      - stores a supplier's information and displays it
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
from contextlib import redirect_stdout

#Each class is kept in its own file (module) and imported here
from supplier import Supplier
from product import Product
from can_be_shipped import CanBeShipped
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory

#inventory.json is kept in the same folder as this script, so it is found
#no matter which folder the program is run from
INVENTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


# File Handling: turn a saved "supplier" dictionary back into a Supplier object.
# Products that share a supplier ID are given the SAME Supplier object, so one
# supplier supplies many products (Supplier 1 ---- 0..* Product), just like
# before the inventory was saved.
# Products saved before Lab 8 have no supplier, so they share an "Unknown Supplier".
def load_supplier(item, suppliers):
    data = item.get("supplier", {"id": "S000", "name": "Unknown Supplier", "contact_email": "-"})
    supplier_id = data["id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, data["name"], data["contact_email"])
    return suppliers[supplier_id]


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
        suppliers = {}  #supplier ID -> Supplier object already created while loading
        for item in items:
            supplier = load_supplier(item, suppliers)
            #Products saved before Lab 7 have no "type" - they were all physical items,
            #so they load as physical products with an unknown (0 kg) weight
            product_type = item.get("type", "physical")
            if product_type == "physical":
                product = PhysicalProduct(item["id"], item["name"], item["price"], item["stock"], supplier, item.get("weight", 0))
            elif product_type == "digital":
                product = DigitalProduct(item["id"], item["name"], item["price"], item["stock"], supplier, item["download_size"])
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
# The Supplier object is saved as a nested dictionary of its details.
# Returns True if saved, False if the file could not be written.
def save_inventory(inventory):
    items = []
    for product in inventory.get_products():
        item = {
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
            "supplier": {
                "id": product.get_supplier().get_supplier_id(),
                "name": product.get_supplier().get_name(),
                "contact_email": product.get_supplier().get_contact_email(),
            },
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


# Find a Supplier that is already linked to a product in the inventory.
# Returns the Supplier object, or None if no product uses that supplier ID.
def find_existing_supplier(inventory, supplier_id):
    for product in inventory.get_products():
        if product.get_supplier().get_supplier_id().upper() == supplier_id.upper():
            return product.get_supplier()
    return None


# Ask for the product's supplier. If the supplier ID is already used, the existing
# Supplier object is reused (one supplier can supply many products). Otherwise a new,
# independent Supplier object is created from the details the user enters.
# Returns a Supplier object, or None if the details were invalid.
def get_supplier_menu(inventory):
    supplier_id = input("Supplier ID: ").strip().upper()
    if supplier_id == "":
        print("Supplier ID cannot be empty.")
        return None
    supplier = find_existing_supplier(inventory, supplier_id)
    if supplier is not None:
        print("Existing supplier found: " + supplier.get_name())
        return supplier

    supplier_name = input("Supplier Name: ").strip()
    if supplier_name == "":
        print("Supplier name cannot be empty.")
        return None
    contact_email = input("Supplier Contact Email: ").strip()
    if "@" not in contact_email:
        print("Invalid email address.")
        return None
    return Supplier(supplier_id, supplier_name, contact_email)


# Menu option 2: ask for the product type and details, create a PhysicalProduct
# or DigitalProduct object (with its Supplier) and pass it to the Inventory
def add_product_menu(inventory):
    print("Add New Product")
    product_type = get_product_type()
    product_id = input("Product ID: ").strip().upper()
    if product_id == "":
        print("Product ID cannot be empty.")
        return
    if inventory.find_product(product_id) is not None:
        print("Product ID " + product_id + " already exists.")
        return

    name = input("Product Name: ").strip()
    if name == "":
        print("Product name cannot be empty.")
        return

    price = get_valid_number("Price: ")
    stock = get_valid_stock("Stock Quantity: ")

    #The Supplier object is created (or found) first, then passed to the Product
    supplier = get_supplier_menu(inventory)
    if supplier is None:
        return

    #Ask for the extra attribute that belongs to the chosen product type
    if product_type == "physical":
        weight = get_valid_number("Weight (kg): ")
        product = PhysicalProduct(product_id, name, price, stock, supplier, weight)
    else:
        download_size = get_valid_number("Download Size (MB): ")
        product = DigitalProduct(product_id, name, price, stock, supplier, download_size)

    inventory.add_product(product)
    print()
    print("Product added successfully!")


# Menu option 3: find the Product and ask it to update its own stock
def update_stock_menu(inventory):
    print("Update Stock")
    product_id = input("Enter Product ID: ").strip()
    print()
    product = inventory.find_product(product_id)
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
    product = inventory.find_product(product_id)
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


# Menu option 5: ask the Inventory to remove the Product's reference.
# Aggregation: the Product object is not destroyed - remove_product() hands it back.
def remove_product_menu(inventory):
    print("Remove Product")
    product_id = input("Enter Product ID: ").strip()
    print()
    product = inventory.remove_product(product_id)
    if product is None:
        print("Product not found.")
        return
    print("Product " + product.get_product_id() + " (" + product.get_name() + ") removed from the inventory.")


def display_menu():
    print()
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Save Inventory")
    print("7. Exit")
    print("----------------------------")


# Testing and review: automatic tests for the Lab 7 checklist and the Lab 8 sections.
# Run with:  python inventory_manager_oop3.py test
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


# Lab 8 - 2.2: test the association between Supplier and Product
def test_supplier_association():
    results = []

    #Create a Supplier object on its own, before any Product exists
    supplier = Supplier("S010", "Global Gadgets", "contact@globalgadgets.com")
    print("Supplier created:")
    supplier.display_information()

    #Create a PhysicalProduct and a DigitalProduct using that same Supplier object
    speaker = PhysicalProduct("P010", "Bluetooth Speaker", 59.90, 30, supplier, 0.8)
    game = DigitalProduct("P011", "Racing Game", 69.00, 500, supplier, 52000)

    #Display the supplier information THROUGH each Product
    print("Supplier information through each Product:")
    for product in [speaker, game]:
        print("  " + product.get_name() + " -> ", end="")
        product.get_supplier().display_information()
    results.append(check("Product stores a reference to its Supplier", speaker.get_supplier() is supplier))
    results.append(check("both products refer to the SAME Supplier object (1 supplier, many products)", speaker.get_supplier() is game.get_supplier()))
    results.append(check("product display shows its supplier", "Supplier: Global Gadgets (S010)" in get_display_output(speaker)))

    #Supplier and Products are separate objects
    print("id(supplier) = " + str(id(supplier)) + " | id(speaker) = " + str(id(speaker)) + " | id(game) = " + str(id(game)))
    results.append(check("Supplier and Products are separate objects", supplier is not speaker and supplier is not game))
    results.append(check("a Supplier exists without needing any Product", isinstance(Supplier("S011", "New Supplier", "new@supplier.com"), Supplier)))

    #Predict first: delete the supplier VARIABLE after creating the products.
    #del only removes the name 'supplier' - the Supplier object is not destroyed,
    #because each Product still holds its own reference to it.
    del supplier
    print("After 'del supplier':")
    for product in [speaker, game]:
        print("  " + product.get_name() + " -> ", end="")
        product.get_supplier().display_information()
    results.append(check("products can still display supplier info after 'del supplier'", speaker.get_supplier().get_name() == "Global Gadgets" and game.get_supplier().get_supplier_id() == "S010"))

    #A Product can exist independently of the Supplier's other products
    del game
    results.append(check("a Product still works when another product of the same supplier is gone", speaker.get_supplier().get_name() == "Global Gadgets"))
    return results


# Lab 8 - 3.2: test the aggregation between Inventory and Product
def test_inventory_aggregation():
    results = []
    supplier = Supplier("S020", "Keyboard World", "info@keyboardworld.com")

    #1. Create a Product BEFORE any Inventory exists
    keyboard = PhysicalProduct("P020", "Mechanical Keyboard", 129.00, 12, supplier, 1.1)
    print("Product created before any Inventory:")
    keyboard.display_information()
    results.append(check("a Product can exist before it is added to an Inventory", keyboard.get_name() == "Mechanical Keyboard"))

    #2. Add the Product to Inventory A
    inventory_a = Inventory()
    results.append(check("add the Product to Inventory A", inventory_a.add_product(keyboard)))
    results.append(check("Inventory A holds a reference to the SAME Product object", inventory_a.find_product("P020") is keyboard))

    #3. Remove it from Inventory A and confirm the Product can still be used
    #Predict first: the Product still works, because remove_product() only removes the
    #reference from Inventory A's list - the Product object itself is not destroyed.
    removed = inventory_a.remove_product("p020")
    results.append(check("remove_product() returns the removed Product", removed is keyboard))
    results.append(check("Inventory A no longer contains the Product", inventory_a.find_product("P020") is None))
    results.append(check("removing an unknown ID returns None", inventory_a.remove_product("P999") is None))
    print("After removing from Inventory A, the Product still works:")
    keyboard.display_information()
    results.append(check("the Product can still be used after removal", keyboard.update_stock(10) and keyboard.get_stock() == 10))

    #4. Add the same Product object to Inventory B (a transfer)
    inventory_b = Inventory()
    results.append(check("the same Product can be added to Inventory B", inventory_b.add_product(keyboard)))
    results.append(check("Inventory B holds the SAME object (not a copy)", inventory_b.find_product("P020") is keyboard))
    results.append(check("the Product kept its updated stock and supplier", inventory_b.find_product("P020").get_stock() == 10 and keyboard.get_supplier() is supplier))

    #5. Emptying an inventory does not destroy its products
    mouse = DigitalProduct("P021", "Mouse Driver", 0.00, 999, supplier, 25)
    inventory_b.add_product(mouse)
    for product in inventory_b.get_products():
        inventory_b.remove_product(product.get_product_id())
    print("After emptying Inventory B:")
    inventory_b.display_all()
    results.append(check("Inventory B is empty", len(inventory_b.get_products()) == 0))
    results.append(check("both products still exist after the inventory is emptied", keyboard.get_name() == "Mechanical Keyboard" and mouse.get_download_size() == 25))

    #Deleting the whole Inventory does not destroy the Product either
    del inventory_a
    results.append(check("the Product still exists after Inventory A is deleted", keyboard.get_product_id() == "P020"))
    return results


def run_tests():
    results = []
    music_supplier = Supplier("S001", "Acme Music Supplies", "sales@acmemusic.com")
    software_supplier = Supplier("S002", "SoftCorp", "orders@softcorp.com")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 8, music_supplier, 3.5)
    operating_system = DigitalProduct("P006", "Operating System", 139.99, 100, software_supplier, 4500)

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
        Product("P001", "Laptop", 1200.00, 15, music_supplier)
        results.append(check("Product cannot be created", False))
    except TypeError as error:
        print("  TypeError: " + str(error))
        results.append(check("Product cannot be created", True))
    print()

    # 5. Physical products can calculate shipping costs ($5.00 base fee + $2.00 per kg)
    print("5. Physical products can calculate shipping costs")
    shipping_tests = [
        (PhysicalProduct("P007", "Headphones", 89.00, 20, music_supplier, 0.5), 6.00),
        (guitar, 12.00),
        (PhysicalProduct("P008", "Amplifier", 499.00, 4, music_supplier, 20), 45.00),
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
    results.append(check("duplicate product ID is rejected", not inventory.add_product(PhysicalProduct("p005", "Other", 1, 1, music_supplier, 1))))
    results.append(check("search finds a product (not case-sensitive)", inventory.find_product("p006") is operating_system))
    results.append(check("search returns None for an unknown ID", inventory.find_product("P999") is None))
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
        loaded_guitar = loaded.find_product("P005")
        loaded_os = loaded.find_product("P006")
        results.append(check("Guitar is loaded back as a PhysicalProduct", type(loaded_guitar) == PhysicalProduct))
        results.append(check("Operating System is loaded back as a DigitalProduct", type(loaded_os) == DigitalProduct))
        results.append(check("weight and updated stock are restored", loaded_guitar.get_weight() == 3.5 and loaded_guitar.get_stock() == 50))
        results.append(check("download size is restored", loaded_os.get_download_size() == 4500))
        results.append(check("saved file has each product's supplier", saved[0]["supplier"]["id"] == "S001" and saved[1]["supplier"]["id"] == "S002"))
        results.append(check("suppliers are loaded back as Supplier objects", type(loaded_guitar.get_supplier()) == Supplier and loaded_os.get_supplier().get_name() == "SoftCorp"))
    finally:
        os.remove(INVENTORY_FILE)
        os.rmdir(os.path.dirname(INVENTORY_FILE))
        INVENTORY_FILE = real_file
    print()

    # Lab 8 - 2.2 Supplier and Product association
    print("Lab 8 - 2.2 Supplier and Product association")
    results.extend(test_supplier_association())
    print()

    # Lab 8 - 3.2 Inventory and Product aggregation
    print("Lab 8 - 3.2 Inventory and Product aggregation")
    results.extend(test_inventory_aggregation())
    print()

    passed = results.count(True)
    print(str(passed) + " of " + str(len(results)) + " tests passed.")
    print("All tests passed!" if passed == len(results) else "Some tests FAILED.")


# Main Program
#Running "python inventory_manager_oop3.py test" runs the tests instead of the menu
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
        remove_product_menu(inventory)
    elif option == "6":
        print("Saving inventory...")
        if save_inventory(inventory):
            print("Inventory saved successfully to inventory.json.")
    elif option == "7":
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
