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
    product_id = input("Product ID: ").strip()
    item = find_product(items, product_id)
    if item is None:
        print("Product not found.")
        return

    print("Current stock for " + item["name"] + ": " + str(item["stock"]))
    try:
        change = int(input("Enter quantity to add (use - to remove, e.g. -5): "))
    except ValueError:
        print("Invalid quantity! Please enter a whole number.")
        return

    if item["stock"] + change < 0:
        print("Not enough stock! Only " + str(item["stock"]) + " units available.")
        return

    item["stock"] = item["stock"] + change
    print()
    print("Stock updated successfully! " + item["name"] + " now has " + str(item["stock"]) + " units.")


def search_product(items):
    print("Search Product")
    keyword = input("Enter Product ID or Name: ").strip().lower()
    results = []
    for item in items:
        if keyword == item["id"].lower() or keyword in item["name"].lower():
            results.append(item)

    print()
    if len(results) == 0:
        print("No matching product found.")
    else:
        display_all(results)


def display_menu():
    print()
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("6. Exit")
    print("----------------------------")


print("=" * 40)
print("INVENTORY MANAGEMENT SYSTEM")
print("=" * 40)

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
    elif option == "6":
        print("Goodbye!")
        break
    else:
        print("Invalid option! Please choose from the menu.")
