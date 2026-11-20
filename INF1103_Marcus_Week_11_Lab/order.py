#Allows the "DiscountStrategy | None" type hint to be written on Python 3.9
from __future__ import annotations

from product import Product
from order_line import OrderLine
from discount_strategy import DiscountStrategy
from no_discount import NoDiscount


#Order class
#SRP: the Order class has one responsibility - represent one customer order and
#manage the order lines that make it up.
#Composition (whole-part, strong ownership): an Order is made up of OrderLine objects
#and OWNS them. The Order CREATES each OrderLine itself inside add_order_line() -
#an OrderLine is never created elsewhere and passed in. Each OrderLine belongs to
#exactly one Order, is never transferred to another Order, and is removed along
#with its Order.
#The Order does NOT own the Products - each OrderLine only refers to a Product.
#UML: Order 1 <filled diamond>---- 0..* OrderLine
#Strategy pattern: the Order is GIVEN a DiscountStrategy and only calls its apply()
#method. It contains no if/elif logic about discount types, so a new kind of discount
#is a new DiscountStrategy class - Order itself never needs to change.
class Order:

    #If no discount strategy is given, the order uses NoDiscount(), so calculate_total()
    #can always call apply() without checking whether a discount exists.
    #(None is used as the default instead of NoDiscount() so each Order gets its own
    #default object rather than sharing one created when the class was defined.)
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id                #unique identifier for the order
        self.__order_lines: list[OrderLine] = []       #the parts this Order owns
        if discount is None:
            discount = NoDiscount()
        self.__discount: DiscountStrategy = discount   #the strategy this Order uses

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    #Change the discount strategy of an existing order - any DiscountStrategy can be
    #swapped in, and Order does not need to know which one it is
    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    #Return a copy of the list, so outside code can read the order lines but cannot
    #add, remove or move OrderLines without going through the Order's own methods
    def get_order_lines(self) -> list[OrderLine]:
        return list(self.__order_lines)

    #Composition: accepts a Product and a quantity (NOT an OrderLine), then the Order
    #creates the OrderLine internally and adds it to its own collection
    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    #Remove an order line through the Order itself - the Order manages its own lines.
    #The OrderLine is discarded with it (it is not returned to be reused or moved to
    #another Order), but the Product it referred to is NOT affected.
    #Returns True if a line for that product ID was removed, False if none was found.
    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id().upper() == product_id.upper():
                self.__order_lines.remove(order_line)
                return True
        return False

    #Value of the order BEFORE any discount: ask each OrderLine to calculate its own
    #subtotal and add them together
    def calculate_subtotal(self) -> float:
        total = 0.0
        for order_line in self.__order_lines:
            total += order_line.calculate_subtotal()
        return total

    #Value of the order AFTER the discount: the order line subtotals are added up and
    #the result is passed to the strategy's apply() method. Order does not know or care
    #which strategy it has - it just calls apply().
    def calculate_total(self) -> float:
        return self.__discount.apply(self.calculate_subtotal())

    #Display the order, each of its order lines and the order total
    def display_information(self) -> None:
        print("Order ID: " + self.__order_id)
        if len(self.__order_lines) == 0:
            print("  No order lines.")
        for order_line in self.__order_lines:
            print("  ", end="")
            order_line.display_information()
        print("  Subtotal: $" + format(self.calculate_subtotal(), ".2f"))
        print("  Discount: " + type(self.__discount).__name__)
        print("  Order Total: $" + format(self.calculate_total(), ".2f"))
