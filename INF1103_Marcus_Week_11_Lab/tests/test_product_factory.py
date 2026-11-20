#Lab 9 - Section 7: Factory pattern tests
#  - Products are created through ProductFactory rather than directly
#  - An unknown product type raises a ValueError with a clear message
import inspect
import unittest

from tests import PROJECT_FOLDER  # noqa: F401  (adds the project folder to sys.path)
from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from product_factory import ProductFactory
import inventory_manager_oop4 as program


class TestProductFactory(unittest.TestCase):

    def setUp(self):
        self.supplier = Supplier("S001", "Test Supplier", "test@supplier.com")

    def test_creates_a_physical_product(self):
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.00, 10, self.supplier, weight=1.2)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertEqual(product.get_weight(), 1.2)

    def test_creates_a_digital_product(self):
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.90, 100, self.supplier, download_size=850)
        self.assertIsInstance(product, DigitalProduct)
        self.assertEqual(product.get_download_size(), 850)

    def test_passes_every_value_to_the_product(self):
        product = ProductFactory.create("physical", "P002", "Chair", 89.50, 4, self.supplier)
        self.assertEqual(product.get_product_id(), "P002")
        self.assertEqual(product.get_name(), "Chair")
        self.assertEqual(product.get_price(), 89.50)
        self.assertEqual(product.get_stock(), 4)
        self.assertIs(product.get_supplier(), self.supplier)

    def test_product_type_is_not_case_sensitive(self):
        self.assertIsInstance(ProductFactory.create(" Digital ", "D002", "Font", 5, 1, self.supplier), DigitalProduct)

    def test_returns_the_base_type_product(self):
        self.assertIn(ProductFactory.create.__annotations__["return"], (Product, "Product"))

    def test_unknown_product_type_raises_value_error_with_clear_message(self):
        with self.assertRaises(ValueError) as caught:
            ProductFactory.create("service", "S001", "Installation", 30.00, 5, self.supplier)
        self.assertEqual(str(caught.exception), "Unknown product type: service")

    def test_program_creates_products_only_through_the_factory(self):
        #The program code (not the tests) must not create product classes directly
        for function in [program.load_inventory, program.add_product_menu, program.load_products]:
            source = inspect.getsource(function)
            self.assertNotIn("PhysicalProduct(", source, function.__name__)
            self.assertNotIn("DigitalProduct(", source, function.__name__)
            self.assertIn("ProductFactory.create(", source, function.__name__)


if __name__ == "__main__":
    unittest.main()
