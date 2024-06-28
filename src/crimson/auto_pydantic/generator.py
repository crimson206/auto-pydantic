from inflection import camelize
from typing import List
from crimson.code_extractor import extract
from crimson.ast_dev_tool import safe_unparse
import ast


def generate_constructor(function_node: ast.FunctionDef, indent: int = 4) -> str:
    """
    # generate_constructor

    ## Description
    The `generate_constructor` function generates a constructor method for a Pydantic model based on the given function node. It creates an `__init__` method that initializes the model's attributes using the function's parameters.

    ## Parameters
    - `function_node` (ast.FunctionDef): An Abstract Syntax Tree (AST) node representing the function for which the constructor is being generated.
    - `indent` (int, optional): The number of spaces to use for indentation. Default is 4.

    ## Returns
    - `str`: A string containing the generated constructor method.

    ## Functionality
    1. Extracts the function specification from the given AST node.
    2. Determines if the function is already an `__init__` method or a regular function.
    3. Generates the method signature with appropriate parameters.
    4. Creates a `super().__init__()` call to initialize the Pydantic model.
    5. Includes all function parameters in the `super().__init__()` call, except for `self` and `cls`.

    ## Example Output
    ```python
    def __init__(self, arg1: int, arg2: str = 'default'):
        super().__init__(arg1=arg1, arg2=arg2)
    ```

    ## Notes
    - The function handles both regular functions and existing `__init__` methods.
    - It properly handles default values and type annotations from the original function.
    - The generated constructor is compatible with Pydantic's model initialization.
    """

    func_spec = extract.extract_func_spec(function_node)
    indent = " " * indent
    if func_spec.name == "__init__":
        start = "def __init__("
    else:
        start = "def __init__(self, "

    def_init = indent + start + safe_unparse(function_node.args) + "):\n"
    super_init = indent * 2 + "super().__init__("
    for arg_spec in func_spec.arg_specs:
        arg_name = arg_spec.name
        if arg_spec.name in ["self", "cls"]:
            continue
        super_init += f"{arg_name}={arg_name}, "
    super_init = super_init[:-2] + ")"

    constructor = def_init + super_init
    return constructor


def generate_input_props(function_node: ast.FunctionDef, constructor: bool = True):
    func_spec = extract.extract_func_spec(function_node)

    input_props_name = _generate_input_props_name(func_spec.name)
    input_props_lines: List[str] = [f"class {input_props_name}(BaseModel):"]
    arg_line_template = "    {arg_name}: {annotation} = {field}"

    for arg_spec in func_spec.arg_specs:
        if arg_spec.name in ["self", "cls"]:
            continue

        annotation = arg_spec.annotation if arg_spec.annotation is not None else "Any"

        if arg_spec.default is not None:
            field = f"Field(default={repr(arg_spec.default)})"
        elif arg_spec.type == "vararg":
            field = "Field(default=())"
        elif arg_spec.type == "kwarg":
            field = "Field(default={})"
        else:
            field = "Field(...)"

        arg_line = arg_line_template.format(arg_name=arg_spec.name, annotation=annotation, field=field)
        input_props_lines.append(arg_line)

    input_props = "\n".join(input_props_lines)

    if constructor is True:
        constructor = generate_constructor(function_node)
        input_props += "\n\n" + constructor

    return input_props


def generate_output_props(function_node: ast.FunctionDef):
    func_spec = extract.extract_func_spec(function_node)
    Func_name = camelize(func_spec.name, uppercase_first_letter=True)

    output_props_lines: List[str] = [f"class {Func_name}OutputProps(BaseModel):"]
    arg_line_template = "    return: {annotation}"

    annotation = func_spec.return_annotation if func_spec.return_annotation is not None else "Any"

    arg_line = arg_line_template.format(
        annotation=annotation,
    )

    output_props_lines.append(arg_line)
    output_props = "\n".join(output_props_lines)
    return output_props


def _generate_input_props_name(func_name: str) -> str:
    Func_name = camelize(func_name, uppercase_first_letter=True)
    input_props_name = f"{Func_name}InputProps"
    return input_props_name
