# !bin/bash

read -p "Please enter the Python version you want to use (e.g., 3.9): " PYTHON_VERSION

conda create --name auto-pydantic python=$PYTHON_VERSION -y

conda activate auto-pydantic

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_dev.txt
