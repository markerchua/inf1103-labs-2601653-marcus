#Lab 9 - Section 7: Validation tests
#  - Invalid prices, stock quantities and order quantities are rejected
import unittest

from tests import PROJECT_FOLDER  # noqa: F401  (adds the project folder to sys.path)
from supplier import Supplier
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from product_factory import ProductFactory
from order import Order
from order_line import OrderLine


class TestProductValidation(unittest.TestCase):

    def setUp(self):
        self.supplier = Supplier("S001", "Test Supplier", "test@supplier.com")

    def test_price_of_zero_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            PhysicalProduct("P001", "Free Pen", 0, 10, self.supplier, 0.1)
        self.assertEqual(str(caught.exception), "Price must be greater than zero.")

    def test_negative_price_is_rejected(self):
        with self.assertRaises(ValueError):
            DigitalProduct("D001", "App", -5.00, 10, self.supplier, 50)

    def test_price_that_is_not_a_number_is_rejected(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P002", "Chair", "abc", 3, self.supplier)

    def test_negative_stock_is_rejected_for_both_product_types(self):
        #LSP: both subclasses follow the SAME rule from Product
        with self.assertRaises(ValueError) as caught:
            PhysicalProduct("P003", "Desk", 120, -1, self.supplier, 20)
        self.assertEqual(str(caught.exception), "Stock quantity cannot be negative.")
        with self.assertRaises(ValueError):
            DigitalProduct("D002", "Game", 20, -3, self.supplier, 900)

    def test_valid_edge_values_are_accepted(self):
        out_of_stock = PhysicalProduct("P004", "Lamp", 25, 0, self.supplier, 1)
        cheap = DigitalProduct("D003", "Sticker", 0.01, 5, self.supplier, 1)
        self.assertEqual(out_of_stock.get_stock(), 0)
        self.assertEqual(cheap.get_price(), 0.01)


class TestOrderLineValidation(unittest.TestCase):

    def setUp(self):
        supplier = Supplier("S001", "Test Supplier", "test@supplier.com")
        self.pen = PhysicalProduct("P001", "Pen", 2.50, 100, supplier, 0.02)

    def test_quantity_of_zero_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            OrderLine(self.pen, 0)
        self.assertEqual(str(caught.exception), "Quantity must be greater than zero.")

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            OrderLine(self.pen, -2)

    def test_rejected_line_is_not_added_to_the_order(self):
        order = Order("O001")
        with self.assertRaises(ValueError):
            order.add_order_line(self.pen, 0)
        self.assertEqual(len(order.get_order_lines()), 0)

    def test_quantity_of_one_is_accepted(self):
        order = Order("O002")
        order.add_order_line(self.pen, 1)
        self.assertEqual(order.calculate_total(), 2.50)


if __name__ == "__main__":
    unittest.main()
