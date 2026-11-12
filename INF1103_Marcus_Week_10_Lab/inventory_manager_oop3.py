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

#Allows the "Supplier | None" type hint to be written on Python 3.9 (built in from 3.10)
from __future__ import annotations

import inspect
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
from order import Order
from order_line import OrderLine

#inventory.json is kept in the same folder as this script, so it is found
#no matter which folder the program is run from
INVENTORY_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


# File Handling: turn a saved "supplier" dictionary back into a Supplier object.
# Products that share a supplier ID are given the SAME Supplier object, so one
# supplier supplies many products (Supplier 1 ---- 0..* Product), just like
# before the inventory was saved.
# Products saved before Lab 8 have no supplier, so they share an "Unknown Supplier".
# item is one product record read from inventory.json (a dictionary).
def load_supplier(item: dict, suppliers: dict[str, Supplier]) -> Supplier:
    data = item.get("supplier", {"id": "S000", "name": "Unknown Supplier", "contact_email": "-"})
    supplier_id = data["id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, data["name"], data["contact_email"])
    return suppliers[supplier_id]


# File Handling: load inventory.json if it exists and use each saved product's
# "type" to create the right subclass (PhysicalProduct or DigitalProduct).
# Otherwise, begin with an empty inventory.
# Returns an Inventory object.
def load_inventory() -> Inventory:
    inventory: Inventory = Inventory()
    if not os.path.exists(INVENTORY_FILE):
        print("inventory.json not found.")
        print("Starting with an empty inventory.")
        return inventory

    print("inventory.json found.")
    try:
        with open(INVENTORY_FILE, "r") as file:
            items = json.load(file)
        suppliers: dict[str, Supplier] = {}  #supplier ID -> Supplier object already created while loading
        for item in items:
            supplier = load_supplier(item, suppliers)
            #Products saved before Lab 7 have no "type" - they were all physical items,
            #so they load as physical products with an unknown (0 kg) weight
            product_type: str = item.get("type", "physical")
            product: Product   #either subclass can be stored in a Product variable
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
def save_inventory(inventory: Inventory) -> bool:
    items: list[dict] = []
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
def get_valid_number(prompt: str) -> float:
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
def get_valid_stock(prompt: str) -> int:
    while True:
        stock = input(prompt)
        if stock.isdigit():
            return int(stock)
        print("Invalid quantity! We only accept positive whole numbers.")


# Keep asking until the user chooses a product type: 1 = physical, 2 = digital
def get_product_type() -> str:
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
def find_existing_supplier(inventory: Inventory, supplier_id: str) -> Supplier | None:
    for product in inventory.get_products():
        if product.get_supplier().get_supplier_id().upper() == supplier_id.upper():
            return product.get_supplier()
    return None


# Ask for the product's supplier. If the supplier ID is already used, the existing
# Supplier object is reused (one supplier can supply many products). Otherwise a new,
# independent Supplier object is created from the details the user enters.
# Returns a Supplier object, or None if the details were invalid.
def get_supplier_menu(inventory: Inventory) -> Supplier | None:
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
def add_product_menu(inventory: Inventory) -> None:
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
def update_stock_menu(inventory: Inventory) -> None:
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
def search_product_menu(inventory: Inventory) -> None:
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
def remove_product_menu(inventory: Inventory) -> None:
    print("Remove Product")
    product_id = input("Enter Product ID: ").strip()
    print()
    product = inventory.remove_product(product_id)
    if product is None:
        print("Product not found.")
        return
    print("Product " + product.get_product_id() + " (" + product.get_name() + ") removed from the inventory.")


def display_menu() -> None:
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
def check(description: str, passed: bool) -> bool:
    print("  " + ("PASS" if passed else "FAIL") + " - " + description)
    return passed


# Capture everything a product's display_information() prints, so it can be checked
def get_display_output(product: Product) -> str:
    captured = io.StringIO()
    with redirect_stdout(captured):
        product.display_information()
    return captured.getvalue()


# Lab 8 - 2.2: test the association between Supplier and Product
def test_supplier_association() -> list[bool]:
    results: list[bool] = []

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
def test_inventory_aggregation() -> list[bool]:
    results: list[bool] = []
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


# Lab 8 - 4.3: test the composition between Order and OrderLine
def test_order_composition() -> list[bool]:
    results: list[bool] = []
    supplier = Supplier("S030", "Studio Gear", "hello@studiogear.com")
    microphone = PhysicalProduct("P030", "Microphone", 120.00, 15, supplier, 0.6)
    recording_software = DigitalProduct("P031", "Recording Software", 199.00, 50, supplier, 1200)
    cable = PhysicalProduct("P032", "XLR Cable", 15.50, 40, supplier, 0.3)

    #The Products also sit in an Inventory - the Orders will only REFER to them
    inventory = Inventory()
    for product in [microphone, recording_software, cable]:
        inventory.add_product(product)

    #Create an Order and add products with add_order_line().
    #Only a Product and a quantity are passed in - the Order creates each OrderLine itself.
    order_1 = Order("O001")
    order_1.add_order_line(microphone, 2)           #2 x $120.00 = $240.00
    order_1.add_order_line(recording_software, 1)   #1 x $199.00 = $199.00
    order_1.add_order_line(cable, 4)                #4 x $15.50  = $62.00
    print("Order 1 with its order lines and total:")
    order_1.display_information()
    results.append(check("the Order created one OrderLine per add_order_line() call", len(order_1.get_order_lines()) == 3))
    results.append(check("the Order calculates its total from its OrderLines ($501.00)", abs(order_1.calculate_total() - 501.00) < 0.001))
    results.append(check("the total equals the sum of each OrderLine's subtotal", abs(order_1.calculate_total() - sum(line.calculate_subtotal() for line in order_1.get_order_lines())) < 0.001))

    #OrderLine refers to the Product but does not own it
    line_1 = order_1.get_order_lines()[0]
    results.append(check("an OrderLine refers to the SAME Product object (not a copy)", line_1.get_product() is microphone))
    results.append(check("that Product is still in the Inventory as well", inventory.find_product("P030") is microphone))

    #Predict first: add the same Product to a different Order.
    #Each Order creates its OWN OrderLine, so there are 2 OrderLine objects,
    #but both refer to the 1 same Product object.
    order_2 = Order("O002")
    order_2.add_order_line(microphone, 1)
    print("Order 2 with the same Microphone:")
    order_2.display_information()
    line_2 = order_2.get_order_lines()[0]
    print("OrderLine in Order 1: id = " + str(id(line_1)) + " -> Product id = " + str(id(line_1.get_product())))
    print("OrderLine in Order 2: id = " + str(id(line_2)) + " -> Product id = " + str(id(line_2.get_product())))
    results.append(check("each Order created its own OrderLine (2 different OrderLine objects)", line_1 is not line_2))
    results.append(check("both OrderLines refer to the same 1 Product object", line_1.get_product() is line_2.get_product() is microphone))
    results.append(check("each OrderLine keeps its own quantity (2 and 1)", line_1.get_quantity() == 2 and line_2.get_quantity() == 1))

    #Remove an order line through an Order method
    results.append(check("remove_order_line() removes the XLR Cable line from Order 1", order_1.remove_order_line("p032")))
    results.append(check("removing a product that is not in the order returns False", not order_1.remove_order_line("P999")))
    print("Order 1 after removing the XLR Cable line:")
    order_1.display_information()
    results.append(check("Order 1 now has 2 lines and a total of $439.00", len(order_1.get_order_lines()) == 2 and abs(order_1.calculate_total() - 439.00) < 0.001))
    results.append(check("removing the order line did NOT remove the Product from the Inventory", inventory.find_product("P032") is cable))
    results.append(check("Order 2 is not affected by changes to Order 1", len(order_2.get_order_lines()) == 1))

    #Remove a whole Order from the scenario: its OrderLines go with it,
    #but the Products and the other Order are not affected
    del order_1
    results.append(check("after Order 1 is deleted, the Products still exist in the Inventory", inventory.find_product("P030") is microphone and inventory.find_product("P031") is recording_software))
    results.append(check("after Order 1 is deleted, Order 2 still has its own OrderLine", order_2.get_order_lines()[0].get_product() is microphone))
    return results


# Lab 8 - 6.2: works with ANY Product, using only behaviour every Product must support.
# It never checks whether the product is a PhysicalProduct or DigitalProduct - the
# object itself decides which display_information()/get_fulfilment_info() runs.
def show_product_details(product: Product) -> None:
    product.display_information()
    print(product.get_fulfilment_info())


# Lab 8 - 6: test that PhysicalProduct and DigitalProduct can stand in for Product
def test_liskov_substitution() -> list[bool]:
    results: list[bool] = []
    supplier = Supplier("S040", "Tech Hub", "sales@techhub.com")
    monitor = PhysicalProduct("P040", "Monitor", 249.00, 10, supplier, 4.2)
    antivirus = DigitalProduct("P041", "Antivirus Licence", 49.99, 200, supplier, 350)

    #6.2 Call the SAME function with both subclasses - no changes to the function
    print("show_product_details() with a PhysicalProduct:")
    show_product_details(monitor)
    print("show_product_details() with a DigitalProduct:")
    show_product_details(antivirus)
    for product in [monitor, antivirus]:
        captured = io.StringIO()
        with redirect_stdout(captured):
            show_product_details(product)
        results.append(check("show_product_details() works with a " + type(product).__name__, product.get_fulfilment_info() in captured.getvalue()))

    #6.2 Both types can be added to an Inventory and used by its normal operations
    inventory = Inventory()
    results.append(check("both product types can be added to the same Inventory", inventory.add_product(monitor) and inventory.add_product(antivirus)))
    results.append(check("find_product() returns either product type", inventory.find_product("P040") is monitor and inventory.find_product("P041") is antivirus))
    captured = io.StringIO()
    with redirect_stdout(captured):
        inventory.display_all()
    results.append(check("display_all() shows each product with its own details", "Weight: 4.20 kg" in captured.getvalue() and "Download Size: 350.00 MB" in captured.getvalue()))
    results.append(check("remove_product() works for either product type", inventory.remove_product("P041") is antivirus and inventory.remove_product("P040") is monitor))

    #6.3 Expectation established by Product: update_stock(quantity) accepts any whole
    #number of 0 or more and returns True, rejects anything else and returns False
    #without changing the stock, and get_stock() then returns the new value.
    #Both subclasses inherit update_stock() WITHOUT overriding it, so they keep this meaning.
    print("6.3 Product expectation: update_stock() means the same for every Product")
    for product in [monitor, antivirus]:
        name = type(product).__name__
        accepted = product.update_stock(25) is True and product.get_stock() == 25
        accepted_zero = product.update_stock(0) is True and product.get_stock() == 0
        rejected = product.update_stock(-3) is False and product.update_stock(2.5) is False and product.get_stock() == 0
        results.append(check(name + " accepts valid stock (25 and 0) and returns True", accepted and accepted_zero))
        results.append(check(name + " rejects invalid stock (-3, 2.5), returns False and keeps its stock", rejected))
        results.append(check(name + " get_fulfilment_info() returns a String, as Product promises", type(product.get_fulfilment_info()) == str))

    #6.3 Diagnose: the teammate's proposed DigitalProduct breaks the expectation above.
    #It is only defined here to show WHY it violates LSP - it is not used in the system.
    class ProposedDigitalProduct(DigitalProduct):
        def update_stock(self, quantity: int) -> None:
            raise NotImplementedError("Digital products have no stock")

    proposed = ProposedDigitalProduct("P042", "Ebook", 9.99, 100, supplier, 5)
    try:
        #Code written for Product - it has no reason to expect an error here
        proposed.update_stock(50)
        broke = False
    except NotImplementedError as error:
        print("  Teammate's DigitalProduct: NotImplementedError: " + str(error))
        broke = True
    results.append(check("the teammate's DigitalProduct breaks code that uses Product (violates LSP)", broke))
    return results


# Lab 8 - 7.2: demonstrate polymorphism through the common Product type
def test_polymorphism() -> list[bool]:
    results: list[bool] = []
    supplier = Supplier("S050", "Home Office Co", "support@homeoffice.com")

    #At least one PhysicalProduct and one DigitalProduct in the SAME Inventory
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P050", "Office Chair", 189.00, 6, supplier, 12.5))
    inventory.add_product(DigitalProduct("P051", "Office Suite", 99.00, 300, supplier, 2800))
    inventory.add_product(PhysicalProduct("P052", "Desk Lamp", 39.90, 25, supplier, 1.2))

    #What each product SHOULD produce - used only to check the output afterwards
    expected = {
        "P050": ("Weight: 12.50 kg", "Office Chair requires physical shipping to the customer."),
        "P051": ("Download Size: 2800.00 MB", "Office Suite is delivered digitally via a download link."),
        "P052": ("Weight: 1.20 kg", "Desk Lamp requires physical shipping to the customer."),
    }

    #7.1 / 7.2: ONE loop over the Product collection. No separate loops for each type
    #and no isinstance() - each call is dispatched to the object's own implementation.
    product: Product
    for product in inventory.get_products():
        captured = io.StringIO()
        with redirect_stdout(captured):
            product.display_information()
            print(product.get_fulfilment_info())
        output = captured.getvalue()
        print(output, end="")

        extra_detail, fulfilment = expected[product.get_product_id()]
        results.append(check(product.get_name() + " ran its own display_information() (" + extra_detail + ")", extra_detail in output))
        results.append(check(product.get_name() + " ran its own get_fulfilment_info()", fulfilment in output))
    return results


# Lab 8 - 5.2: check every method of every class has type hints on all of its
# parameters (except self) and on its return value, and that Any is never used.
# Python does not enforce type hints, so this test checks that they are WRITTEN.
def test_type_hints() -> list[bool]:
    results: list[bool] = []
    classes = [Supplier, Product, CanBeShipped, PhysicalProduct, DigitalProduct, Inventory, OrderLine, Order]
    for cls in classes:
        missing: list[str] = []
        uses_any = False
        #Only the methods written in this class (not the ones it inherits)
        for method_name, method in vars(cls).items():
            if not inspect.isfunction(method):
                continue
            hints = method.__annotations__
            for parameter in list(inspect.signature(method).parameters)[1:]:   #[1:] skips self
                if parameter not in hints:
                    missing.append(method_name + "(" + parameter + ")")
            if "return" not in hints:
                missing.append(method_name + "() return type")
            if any("Any" in str(hint) for hint in hints.values()):
                uses_any = True
        description = cls.__name__ + " has type hints on all parameters and return values"
        if missing:
            description += " - missing: " + ", ".join(missing)
        results.append(check(description, not missing and not uses_any))
    return results


def run_tests() -> None:
    results: list[bool] = []
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

    # Lab 8 - 4.3 Order and OrderLine composition
    print("Lab 8 - 4.3 Order and OrderLine composition")
    results.extend(test_order_composition())
    print()

    # Lab 8 - 6 Liskov Substitution Principle
    print("Lab 8 - 6 Liskov Substitution Principle (LSP)")
    results.extend(test_liskov_substitution())
    print()

    # Lab 8 - 7 Polymorphism
    print("Lab 8 - 7 Polymorphism through the Product type")
    results.extend(test_polymorphism())
    print()

    # Lab 8 - 5.2 Review all type decisions
    print("Lab 8 - 5.2 Type hints are present on every class")
    results.extend(test_type_hints())
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
inventory: Inventory = load_inventory()  #Inventory object holding Product objects

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
