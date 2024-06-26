#!bin/bash

coverage run --source=. -m unittest discover -s ./test -p "test_*.py"