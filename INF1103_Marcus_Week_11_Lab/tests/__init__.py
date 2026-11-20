#Automated tests for the Inventory Management System (Lab 9).
#Run from the project folder with:
#    python -m unittest discover -s tests -v
#The command exits with code 0 if every test passes and 1 if any test fails,
#which is what a CI pipeline checks after every push.
import os
import sys

#Let the tests import the project modules (product.py, order.py, ...) that sit
#in the folder ABOVE this tests folder
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_FOLDER not in sys.path:
    sys.path.insert(0, PROJECT_FOLDER)
