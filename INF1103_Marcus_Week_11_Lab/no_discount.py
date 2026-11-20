from discount_strategy import DiscountStrategy


#NoDiscount strategy
#Inheritance: a NoDiscount 'is-a' DiscountStrategy.
#Used when an order has no discount, so Order can ALWAYS call apply() without
#first checking whether a discount exists.
class NoDiscount(DiscountStrategy):

    #Returns the total unchanged
    def apply(self, total: float) -> float:
        return total
