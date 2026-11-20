#Allows the "Product | None" type hint to be written on Python 3.9 (it is built in from 3.10)
from __future__ import annotations

from product import Product


#Inventory class
#SRP: the Inventory class has one responsibility - manage a collection of Product objects.
#It does NOT load/save files, ask the user for input or show the menu.
#Aggregation (whole-part, weak ownership): an Inventory is a whole made up of Product
#parts, but it does NOT create or own them. Products are created elsewhere (the menu,
#load_inventory() or the tests) and then added. They can exist before being added and
#are not destroyed when removed, so the same Product can be moved to another Inventory.
#UML: Inventory 0..1 <>---- 0..* Product
class Inventory:

    #Start with an empty collection that will hold references to Product objects.
    #Type hint list[Product]: typed with the base class Product, not PhysicalProduct or
    #DigitalProduct, so one collection can hold either type (and any future subclass).
    def __init__(self) -> None:
        self.__products: list[Product] = []

    #Add an EXISTING Product object to the inventory - the Inventory only stores a
    #reference to it, it does not create the Product.
    #Returns True if added, False if a product with the same ID already exists.
    def add_product(self, product: Product) -> bool:
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    #Remove the matching Product REFERENCE from the inventory (ID is not case-sensitive).
    #The Product object itself is not destroyed - it is returned so the caller can keep
    #using it, e.g. add it to another Inventory (a transfer).
    #Returns the removed Product, or None if no product has that ID.
    def remove_product(self, product_id: str) -> Product | None:
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    #Find a product by its ID (not case-sensitive).
    #Returns the Product object, or None if not found.
    def find_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_product_id().upper() == product_id.upper():
                return product
        return None

    #Display every product in the inventory.
    #The Inventory only manages the collection - each Product displays its own information.
    def display_all(self) -> None:
        print("Current Inventory")
        print("-" * 45)
        if len(self.__products) == 0:
            print("No products in inventory.")
        for product in self.__products:
            product.display_information()
        print("-" * 45)

    #Return a copy of the product list (e.g. for saving), so outside code
    #cannot add or remove products without going through add_product()/remove_product()
    def get_products(self) -> list[Product]:
        return list(self.__products)
