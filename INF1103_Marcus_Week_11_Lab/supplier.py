#Supplier class
#SRP: the Supplier class has one responsibility - represent a single supplier.
#Association: a Supplier is NOT part of a Product and a Product is NOT part of a Supplier.
#Both are created independently and can exist without each other - they only
#collaborate through a reference ('knows-about', not 'has-a').
#Type hints show the intended type of each attribute, parameter and return value.
#Python does not enforce them, but they document the design shown in the UML diagram.
class Supplier:

    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self.__supplier_id: str = supplier_id        #unique identifier for the supplier
        self.__name: str = name                      #supplier's name
        self.__contact_email: str = contact_email    #supplier's contact email address

    #Getters: let other code (e.g. a Product) read the supplier's details
    #without being able to change them
    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    #A supplier is responsible for providing information about itself
    def display_information(self) -> None:
        print("Supplier ID: " + self.__supplier_id + " | Name: " + self.__name + " | Email: " + self.__contact_email)
