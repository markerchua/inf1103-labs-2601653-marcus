from product import Product
from order_line import OrderLine


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
class Order:

    def __init__(self, order_id: str) -> None:
        self.__order_id: str = order_id                #unique identifier for the order
        self.__order_lines: list[OrderLine] = []       #the parts this Order owns

    def get_order_id(self) -> str:
        return self.__order_id

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

    #Total value of the order: ask each OrderLine to calculate its own subtotal
    #and add them together
    def calculate_total(self) -> float:
        total = 0.0
        for order_line in self.__order_lines:
            total += order_line.calculate_subtotal()
        return total

    #Display the order, each of its order lines and the order total
    def display_information(self) -> None:
        print("Order ID: " + self.__order_id)
        if len(self.__order_lines) == 0:
            print("  No order lines.")
        for order_line in self.__order_lines:
            print("  ", end="")
            order_line.display_information()
        print("  Order Total: $" + format(self.calculate_total(), ".2f"))
