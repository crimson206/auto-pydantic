# auto-pydantic

- Author : Sonnet3.5
- Editor : Sisung Kim

auto-pydantic is a Python module that provides automatic Pydantic model generation and validation for function parameters and return types.

## Features

- Generate Pydantic input models from function signatures
- Generate Pydantic output models from function return types
- Automatic validation of function inputs using generated Pydantic models
- Support for simple and complex function signatures, including *args and **kwargs

## Installation

To install crimson-auto-pydantic, you can use pip:

```
pip install acrimson-auto-pydantic
```

## Usage

### Generating Input Props

```python
from crimson.auto_pydantic.generator import generate_input_props

def my_function(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"

input_props = generate_input_props(my_function)
print(input_props)
```

### Generating Output Props

```python
from crimson.auto_pydantic.generator import generate_output_props

def my_function(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"

output_props = generate_output_props(my_function)
print(output_props)
```

### Validating Function Inputs

```python
from crimson.auto_pydantic.validator import validate
from inspect import currentframe

def my_function(arg1: int, arg2: str = "default") -> str:
    validate(my_function, currentframe(), arg1, arg2)
    return f"{arg1} {arg2}"

# This will pass validation
my_function(1, "test")

# This will raise a validation error
my_function("not an int", "test")
```
