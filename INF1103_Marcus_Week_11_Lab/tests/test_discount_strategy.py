#Lab 9 - Section 7: Strategy pattern tests
#  - Order calculates totals through a DiscountStrategy and contains no discount if/elif logic
#  - A new discount strategy can be added without changing Order
#  - The strategy on an existing order can be changed with set_discount()
import inspect
import unittest

from tests import PROJECT_FOLDER  # noqa: F401  (adds the project folder to sys.path)
from supplier import Supplier
from physical_product import PhysicalProduct
from order import Order
from discount_strategy import DiscountStrategy
from no_discount import NoDiscount
from percentage_discount import PercentageDiscount
from bulk_discount import BulkDiscount
from student_discount import StudentDiscount


class TestDiscountStrategies(unittest.TestCase):

    def test_no_discount_returns_total_unchanged(self):
        self.assertEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount_takes_percentage_off(self):
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_applies_at_or_above_threshold(self):
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(250.0), 230.0)
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(200.0), 180.0)

    def test_bulk_discount_does_not_apply_below_threshold(self):
        self.assertEqual(BulkDiscount(200, 20).apply(199.99), 199.99)

    def test_student_discount_takes_five_percent_off(self):
        self.assertAlmostEqual(StudentDiscount().apply(250.0), 237.5)

    def test_discount_strategy_is_abstract(self):
        with self.assertRaises(TypeError):
            DiscountStrategy()

    def test_invalid_strategy_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            PercentageDiscount(150)
        with self.assertRaises(ValueError):
            PercentageDiscount(-1)
        with self.assertRaises(ValueError):
            BulkDiscount(200, -20)


class TestOrderUsesStrategy(unittest.TestCase):

    #Runs before EVERY test, so each test starts with a fresh order worth 250.00
    def setUp(self):
        supplier = Supplier("S001", "Test Supplier", "test@supplier.com")
        self.headset = PhysicalProduct("P001", "Headset", 100.00, 20, supplier, 0.4)
        self.game = PhysicalProduct("P002", "Game Box", 50.00, 20, supplier, 0.2)
        self.order = Order("O001", BulkDiscount(200, 20))
        self.order.add_order_line(self.headset, 2)
        self.order.add_order_line(self.game, 1)

    def test_order_without_a_strategy_uses_no_discount(self):
        order = Order("O002")
        order.add_order_line(self.headset, 1)
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertEqual(order.calculate_total(), 100.0)

    def test_order_calculates_total_through_its_strategy(self):
        self.assertEqual(self.order.calculate_subtotal(), 250.0)
        self.assertAlmostEqual(self.order.calculate_total(), 230.0)

    def test_set_discount_changes_the_strategy_on_an_existing_order(self):
        self.order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(self.order.calculate_total(), 225.0)
        self.assertEqual(len(self.order.get_order_lines()), 2)   #the lines did not change

    def test_order_contains_no_discount_if_elif_logic(self):
        source = inspect.getsource(Order)
        for word in ["elif", "discount_type", "PercentageDiscount", "BulkDiscount", "StudentDiscount", "isinstance"]:
            self.assertNotIn(word, source)

    def test_new_strategy_works_without_changing_order(self):
        #A brand-new strategy, written ONLY in this test - Order has never seen it
        class HalfPriceDiscount(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        self.order.set_discount(HalfPriceDiscount())
        self.assertAlmostEqual(self.order.calculate_total(), 125.0)

    def test_two_orders_can_share_one_strategy(self):
        shared = PercentageDiscount(10)
        other_order = Order("O003", shared)
        other_order.add_order_line(self.game, 2)
        self.order.set_discount(shared)
        self.assertIs(self.order.get_discount(), other_order.get_discount())
        self.assertAlmostEqual(self.order.calculate_total(), 225.0)
        self.assertAlmostEqual(other_order.calculate_total(), 90.0)


if __name__ == "__main__":
    unittest.main()
