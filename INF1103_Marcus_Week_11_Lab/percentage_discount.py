from discount_strategy import DiscountStrategy


#PercentageDiscount strategy
#Inheritance: a PercentageDiscount 'is-a' DiscountStrategy.
#The percentage is given when the strategy is created, e.g. PercentageDiscount(10)
#takes 10% off - so a 15% or 25% discount needs no new code, just a new object.
class PercentageDiscount(DiscountStrategy):

    def __init__(self, percentage: float) -> None:
        #Validation: a percentage discount only makes sense between 0% and 100%
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage must be between 0 and 100.")
        self.__percentage: float = float(percentage)

    def get_percentage(self) -> float:
        return self.__percentage

    #Takes the percentage off the total, e.g. 10% off 250.00 = 225.00
    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)
