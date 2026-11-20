from abc import ABC, abstractmethod


#CanBeShipped interface
#Python has no interface keyword, so an abstract base class is used as an
#interface-style contract. This is a 'must be able to' relationship, not 'is-a':
#any class that implements CanBeShipped must be able to calculate its shipping cost.
#It has no attributes or shipping details, so any shippable object can sign the contract.
class CanBeShipped(ABC):

    #Implementing classes must provide a way to calculate shipping costs
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass
