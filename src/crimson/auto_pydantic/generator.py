from inflection import camelize
from typing import List, Generic, TypeVar, Union, Callable
from crimson.code_extractor import extract
from crimson.ast_dev_tool import safe_unparse, collect_nodes
from crimson.intelli_type import IntelliType
from inspect import getsource
import ast

T = TypeVar("T")


class Function_(IntelliType[Union[Callable, str, ast.FunctionDef]], Generic[T]):
    """
    A versatile representation of a function that can handle various input types.

    Example:
        def func(arg1: int):
            return arg1

        This class can handle any of the followings:
        - func
        - inspect.getsource(func)
        - ast.parse(inspect.getsource(func)).body[0]

    Key features:
        - Robust handling of functions, even when they're not the first item in a module
        - Capable of processing modules with multiple function definitions
        - All auto-pydantic functions are designed to work flexibly with this class
        - When multiple functions are present, the first function is used by default

    Note: This flexibility allows for easier integration and usage across different
    scenarios in the auto-pydantic module.
    """


class Constructor_(IntelliType[str], Generic[T]):
    """
    Represents the constructor code for a Pydantic model.

    This class encapsulates the string representation of a Pydantic model's constructor.
    It allows the model to mirror the structure of the original function it's based on.

    Example:
        Original function:
            def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs) -> str:
                return "bye"

        Corresponding constructor:
            def __init__(self, arg1: int, *args: Tuple[int, int], arg2: str='hi', arg3: int=1, **kwargs):
                super().__init__(arg1=arg1, args=args, arg2=arg2, arg3=arg3, kwargs=kwargs)

    This constructor ensures that the Pydantic model can be instantiated with the same
    signature as the original function, maintaining consistency in parameter handling.
    """


class InputProps_(IntelliType[str], Generic[T]):
    """
    Represents the input properties of a Pydantic model based on a function's parameters.

    This class contains the string representation of a Pydantic model class that
    encapsulates the input parameters of a target function.

    Example:
    For the function:
        def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs) -> str:
            return "bye"

    The corresponding InputProps model would be:
        class Func2InputProps(BaseModel):
            arg1: int = Field(...)
            args: Tuple[int, int] = Field(default=())
            arg2: str = Field(default="'hi'")
            arg3: int = Field(default='1')
            kwargs: Any = Field(default={})

            {optional_constructor}

    Note: The {optional_constructor} placeholder can be replaced with an actual
    constructor if needed, allowing for flexible model creation.
    """


class OutputProps_(IntelliType[str], Generic[T]):
    """
    Represents the output properties of a Pydantic model based on a function's return type.

    This class contains the string representation of a Pydantic model class that
    encapsulates the return type of a target function.

    Example:
        For the function:
        def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs) -> str:
            return "bye"

    The corresponding OutputProps model would be:
        class Func2OutputProps(BaseModel):
            return: str

    This model standardizes the function's output, making it easier to validate
    and work with the return value in a type-safe manner.
    """


def generate_constructor(
    function: Union[Callable, str, ast.FunctionDef], indent: int = 4
) -> Constructor_[str]:
    """
    Generate a constructor string for a Pydantic model based on the given function.

    This function creates a constructor that mirrors the input function's signature,
    allowing for seamless integration with Pydantic models.
    """
    function_node = _convert_to_FunctionDef(function)
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


def generate_input_props(
    function: Function_[Union[Callable, str, ast.FunctionDef]], add_constructor: bool = True
) -> InputProps_[str]:
    """
    Generate input properties string for a Pydantic model based on the given function.

    This function creates a Pydantic model class that represents the input parameters
    of the given function, including type annotations and default values.
    """
    function_node: ast.FunctionDef = _convert_to_FunctionDef(function)
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

    if add_constructor is True:
        add_constructor = generate_constructor(function_node)
        input_props += "\n\n" + add_constructor

    return input_props


def generate_output_props(function: Function_[Union[Callable, str, ast.FunctionDef]]) -> OutputProps_[str]:
    """
    Generate output properties string for a Pydantic model based on the given function.

    This function creates a Pydantic model class that represents the return type
    of the given function, encapsulating the output in a standardized format.
    """
    function_node = _convert_to_FunctionDef(function)

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


def _convert_to_FunctionDef(function: Function_[Union[Callable, str, ast.FunctionDef]]) -> ast.FunctionDef:
    if type(function) is Callable:
        function = getsource(function)

    if type(function) is str:
        function = ast.parse(function)

    function_node: ast.FunctionDef = collect_nodes(function, ast.FunctionDef)[0]

    return function_node
