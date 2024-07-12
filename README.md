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
pip install crimson-auto-pydantic
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
Output:
```
class MyFunctionInputProps(BaseModel):
    arg1: int = Field(...)
    arg2: str = Field(default="'default'")

    def __init__(self, arg1: int, arg2: str='default'):
        super().__init__(arg1=arg1, arg2=arg2)
```

### Generating Output Props

```python
from crimson.auto_pydantic.generator import generate_output_props

def my_function(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"

output_props = generate_output_props(my_function)
print(output_props)
```
Output:
```
class MyFunctionOutputProps(BaseModel):
    return: str
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
Validation Error:
```
ValidationError: 1 validation error for MyFunctionInputProps
arg1
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not an int', input_type=str]
    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing
```