from abc import ABC, abstractmethod


#DiscountStrategy abstract class (Strategy pattern)
#Problem: one task - discounting an order total - can be done in several different ways.
#Instead of an if/elif block in Order, each way of discounting is moved into its own
#class. Every strategy provides the same apply() method, so the class that uses a
#strategy (Order) only calls apply() and never needs to know how the discount works.
#A new discount means a new class, not a change to Order (Open/Closed Principle).
#Abstract class: a generic DiscountStrategy cannot be created - only real strategies can.
class DiscountStrategy(ABC):

    #Takes the order total and returns the discounted total
    @abstractmethod
    def apply(self, total: float) -> float:
        pass
