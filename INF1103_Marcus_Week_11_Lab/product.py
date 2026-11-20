from abc import ABC, abstractmethod

from supplier import Supplier


#Product class
#SRP: the Product class has one responsibility - represent and manage a single product.
#It does NOT load/save files, ask the user for input, show the menu or manage the inventory.
#Abstract class: Product inherits from ABC and has an abstract method, so a generic
#Product can never be created directly - every product must be a PhysicalProduct or
#a DigitalProduct.
#Association: every Product knows about the one Supplier that supplies it. The Supplier
#is created independently and passed in - the Product does not create or own it, and the
#Supplier is not 'part of' the Product. Both objects can exist without each other.
class Product(ABC):

    #Initializer (constructor): the parameters are the values passed in from outside,
    #the self.__ attributes belong to this object. The double underscore marks them as
    #private, so outside code should use the public methods below instead.
    #Type hints show the intended types. supplier: Supplier means the constructor expects
    #a Supplier OBJECT, not just the supplier's name or ID.
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier) -> None:
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = float(price)
        self.__stock: int = int(stock)
        self.__supplier: Supplier = supplier   #reference to an existing Supplier object

    #Getters: let other code read the attributes without being able to change them
    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    #Returns the Supplier object itself, so its information can be accessed when required
    def get_supplier(self) -> Supplier:
        return self.__supplier

    #Encapsulation: the stock can only be changed through this method, so the Product
    #decides whether the new value is allowed before assigning it to self.__stock.
    #Returns True if the stock was updated, False if the quantity was rejected.
    def update_stock(self, quantity: int) -> bool:
        if type(quantity) != int or quantity < 0:
            return False
        self.__stock = quantity
        return True

    #Display this product's information, including who supplies it.
    #The supplier's details are read through the stored Supplier reference.
    def display_information(self) -> None:
        print("ID: " + self.__product_id + " | Name: " + self.__name + " | Price: $" + format(self.__price, ".2f") + " | Stock: " + str(self.__stock))
        print("      Supplier: " + self.__supplier.get_name() + " (" + self.__supplier.get_supplier_id() + ")")

    #Abstract method: no implementation here. Every subclass must provide its own
    #get_fulfilment_info() explaining how that type of product reaches the customer.
    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass
