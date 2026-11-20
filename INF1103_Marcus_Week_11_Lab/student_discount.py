from discount_strategy import DiscountStrategy


#StudentDiscount strategy (Lab 9 - 2.4 Extend without modifying)
#Inheritance: a StudentDiscount 'is-a' DiscountStrategy.
#The business wants a 5% student discount. With the Strategy pattern this is a NEW
#class - Order did not need to change at all, because Order only calls apply().
#This is the Open/Closed Principle: open for extension, closed for modification.
class StudentDiscount(DiscountStrategy):

    #Fixed student rate, kept in one place
    STUDENT_PERCENTAGE: float = 5.0

    #Takes 5% off the total, e.g. 250.00 -> 237.50
    def apply(self, total: float) -> float:
        return total * (1 - self.STUDENT_PERCENTAGE / 100)
