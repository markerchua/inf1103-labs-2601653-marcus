from discount_strategy import DiscountStrategy


#BulkDiscount strategy
#Inheritance: a BulkDiscount 'is-a' DiscountStrategy.
#Takes a fixed amount off any order total that reaches a threshold,
#e.g. BulkDiscount(200, 20) takes 20 off any total of 200 or more.
class BulkDiscount(DiscountStrategy):

    def __init__(self, threshold: float, amount: float) -> None:
        #Validation: neither the threshold nor the amount can be negative
        if threshold < 0 or amount < 0:
            raise ValueError("Threshold and amount cannot be negative.")
        self.__threshold: float = float(threshold)
        self.__amount: float = float(amount)

    def get_threshold(self) -> float:
        return self.__threshold

    def get_amount(self) -> float:
        return self.__amount

    #Only totals that reach the threshold get the discount
    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount
        return total
