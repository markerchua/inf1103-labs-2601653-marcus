#Lab 9 - Section 7: Exception handling tests
#  - Invalid user input is handled without crashing, and the user is asked again
#  - A missing products file is handled gracefully
#  - Bad rows in the products file are reported and skipped, and valid rows still load
#  - Each except catches a specific exception
import ast
import glob
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from tests import PROJECT_FOLDER
from supplier import Supplier
from inventory import Inventory
import inventory_manager_oop4 as program


#Run function(prompt) while input() returns each of typed_values in turn.
#Returns (what the function returned, every line it printed).
def run_with_typed_input(function, typed_values):
    captured = io.StringIO()
    with patch("builtins.input", side_effect=typed_values), redirect_stdout(captured):
        result = function("Enter: ")
    return result, captured.getvalue().splitlines()


#Run load_products() and return (inventory, every line it printed)
def run_load_products(path):
    inventory = Inventory()
    supplier = Supplier("S001", "CSV Supplier", "csv@supplier.com")
    captured = io.StringIO()
    with redirect_stdout(captured):
        program.load_products(path, inventory, supplier)
    return inventory, captured.getvalue().splitlines()


class TestUserInput(unittest.TestCase):

    def test_text_then_negative_then_valid_price(self):
        value, lines = run_with_typed_input(program.get_positive_float, ["abc", "-5", "12.50"])
        self.assertEqual(lines, ["Please enter a valid number, e.g. 12.50",
                                 "Please enter a number greater than zero."])
        self.assertEqual(value, 12.5)

    def test_zero_and_empty_input_are_asked_again(self):
        value, lines = run_with_typed_input(program.get_positive_float, ["0", "", "3"])
        self.assertEqual(len(lines), 2)
        self.assertEqual(value, 3.0)

    def test_stock_input_no_longer_crashes_on_superscript_two(self):
        value, lines = run_with_typed_input(program.get_valid_stock, ["²", "-1", "2.5", "7"])
        self.assertEqual(value, 7)
        self.assertEqual(len(lines), 3)


class TestLoadProducts(unittest.TestCase):

    def test_products_csv_loads_valid_rows_and_skips_bad_rows(self):
        inventory, lines = run_load_products(program.PRODUCTS_FILE)
        loaded_ids = [product.get_product_id() for product in inventory.get_products()]
        self.assertEqual(loaded_ids, ["P001", "D001", "P003"])
        self.assertIn("Unknown product type: service", lines[0])
        self.assertIn("could not convert string to float: 'abc'", lines[1])
        self.assertEqual(lines[2:], ["3 products loaded.", "Load attempt finished."])

    def test_missing_file_is_handled_gracefully(self):
        missing = os.path.join(tempfile.gettempdir(), "this_file_does_not_exist.csv")
        inventory, lines = run_load_products(missing)
        #except and finally run - else does not
        self.assertEqual(lines, ["Products file not found: " + missing, "Load attempt finished."])
        self.assertEqual(len(inventory.get_products()), 0)

    def test_rows_with_missing_columns_or_broken_rules_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "bad_products.csv")
            with open(path, "w", newline="") as file:
                file.write("product_type,product_id,name,price,stock_quantity\n")
                file.write("physical,P900,Missing Stock,10.00\n")
                file.write("physical,P901,Free Item,0,5\n")
                file.write("digital,D900,Negative Stock,5.00,-1\n")
                file.write("digital,D901,Good Item,5.00,1\n")
                file.write("digital,D901,Duplicate Item,5.00,1\n")
            inventory, lines = run_load_products(path)
        self.assertEqual(sum(line.startswith("Skipped line") for line in lines), 4)
        self.assertIn("1 products loaded.", lines)
        self.assertIsNotNone(inventory.find_product("D901"))


class TestSpecificExceptions(unittest.TestCase):

    def test_every_except_names_a_specific_exception(self):
        #Read every .py file in the project and check each except clause.
        #A bare "except:" or "except Exception:" would hide unexpected errors.
        python_files = glob.glob(os.path.join(PROJECT_FOLDER, "*.py")) + glob.glob(os.path.join(PROJECT_FOLDER, "tests", "*.py"))
        for path in python_files:
            with open(path, encoding="utf-8") as file:
                tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    where = os.path.basename(path) + " line " + str(node.lineno)
                    self.assertIsNotNone(node.type, "bare except in " + where)
                    names = [ast.unparse(node.type)] if not isinstance(node.type, ast.Tuple) else [ast.unparse(e) for e in node.type.elts]
                    for name in names:
                        self.assertNotIn(name, ("Exception", "BaseException"), "too general in " + where)


if __name__ == "__main__":
    unittest.main()
