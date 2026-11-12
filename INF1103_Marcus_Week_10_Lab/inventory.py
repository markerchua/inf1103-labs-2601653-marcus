from product import Product


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
