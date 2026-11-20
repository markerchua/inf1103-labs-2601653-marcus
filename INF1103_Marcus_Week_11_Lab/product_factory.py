from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from supplier import Supplier


#ProductFactory class (Factory pattern)
#Problem: without a factory, every part of the program that needs a product creates a
#PhysicalProduct or DigitalProduct directly, so that code must know about every product
#class and must change whenever a new product type is added.
#Solution: the factory OWNS the creation decision. The rest of the program asks the
#factory for a product by its type name, and gets back a Product - it only needs to know
#about Product and the factory, which reduces coupling.
#Trade-off: the factory itself still changes when a new type is added (it breaks OCP),
#but that change is now in ONE place. For a small system this is simpler than more
#complicated designs such as registering each type with the factory.
#Dependency: the factory creates products but does not store them.
#UML: ProductFactory - - - «creates» - - -> Product
class ProductFactory:

    #Static method: no ProductFactory object is needed - call ProductFactory.create(...).
    #weight is only used by physical products and download_size only by digital products.
    #Both default to 0.0 so a product can still be created when that detail is unknown
    #(e.g. from a file that does not include it).
    #Returns the type Product, not PhysicalProduct or DigitalProduct.
    #Raises ValueError if the product type is unknown.
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               weight: float = 0.0, download_size: float = 0.0) -> Product:
        product_type = product_type.strip().lower()   #"Physical " -> "physical"
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError("Unknown product type: " + product_type)
