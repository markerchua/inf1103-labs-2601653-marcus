from product import Product
from supplier import Supplier


#DigitalProduct class
#Inheritance: a DigitalProduct 'is-a' Product, so it inherits all of Product's
#attributes and methods. It has no weight, but adds a download size instead.
class DigitalProduct(Product):

    #Reuse the Product constructor with super() to set up the ID, name, price, stock and
    #supplier, then initialise the extra download_size attribute
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, download_size: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size = float(download_size)   #float, in megabytes

    def get_download_size(self):
        return self.__download_size

    #Method overriding: replaces Product's display_information() for digital products.
    #super() lets the parent display the common product information, then the child
    #only adds the part that is unique to it - the download size.
    def display_information(self):
        super().display_information()
        print("      Download Size: " + format(self.__download_size, ".2f") + " MB")

    #Implements Product's abstract method: digital products are delivered digitally
    def get_fulfilment_info(self):
        return self.get_name() + " is delivered digitally via a download link."
