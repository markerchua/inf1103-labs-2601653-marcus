from product import Product
from supplier import Supplier
from can_be_shipped import CanBeShipped


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

    #Reuse the Product constructor with super() to set up the ID, name, price, stock and
    #supplier, then initialise the extra weight attribute
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
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
