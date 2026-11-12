from product import Product


#OrderLine class
#SRP: the OrderLine class has one responsibility - represent ONE product and the
#quantity of it requested within an order, and calculate that line's subtotal.
#Composition (part): an OrderLine is part of exactly one Order. It is created and
#managed by its Order (Order.add_order_line()), never created elsewhere and passed in,
#and it is not transferred to another Order. If the Order is removed, its OrderLines go too.
#Association: an OrderLine only REFERS to a Product - it does not own it. The Product
#exists independently, may also be in an Inventory, and may appear in many orders.
#UML: Order 1 <filled diamond>---- 0..* OrderLine,   OrderLine 0..* ---- 1 Product
class OrderLine:

    #Type hints: product is a reference to a Product object (either subclass),
    #quantity is a whole number
    def __init__(self, product: Product, quantity: int) -> None:
        self.__product: Product = product      #reference to an existing Product
        self.__quantity: int = int(quantity)   #how many of the product were ordered

    #Getters: let other code read the order line without being able to change it
    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    #Subtotal for this line = the product's price x the quantity ordered
    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    #Display this order line on one line
    def display_information(self) -> None:
        print(self.__product.get_product_id() + " | " + self.__product.get_name() + " | " + str(self.__quantity) + " x $" + format(self.__product.get_price(), ".2f") + " = $" + format(self.calculate_subtotal(), ".2f"))
