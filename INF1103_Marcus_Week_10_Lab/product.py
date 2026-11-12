from abc import ABC, abstractmethod


#Product class
#SRP: the Product class has one responsibility - represent and manage a single product.
#It does NOT load/save files, ask the user for input, show the menu or manage the inventory.
#Abstract class: Product inherits from ABC and has an abstract method, so a generic
#Product can never be created directly - every product must be a PhysicalProduct or
#a DigitalProduct.
class Product(ABC):

    #Initializer (constructor): the parameters are the values passed in from outside,
    #the self.__ attributes belong to this object. The double underscore marks them as
    #private, so outside code should use the public methods below instead.
    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id  #String
        self.__name = name              #String
        self.__price = float(price)     #float
        self.__stock = int(stock)       #int

    #Gett
    # ers: let other code read the attributes without being able to change them
    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    #Encapsulation: the stock can only be changed through this method, so the Product
    #decides whether the new value is allowed before assigning it to self.__stock.
    #Returns True if the stock was updated, False if the quantity was rejected.
    def update_stock(self, quantity):
        if type(quantity) != int or quantity < 0:
            return False
        self.__stock = quantity
        return True

    #Display this product's information on one line
    def display_information(self):
        print("ID: " + self.__product_id + " | Name: " + self.__name + " | Price: $" + format(self.__price, ".2f") + " | Stock: " + str(self.__stock))

    #Abstract method: no implementation here. Every subclass must provide its own
    #get_fulfilment_info() explaining how that type of product reaches the customer.
    @abstractmethod
    def get_fulfilment_info(self):
        pass
