from inflection import camelize
from typing import List, Generic, TypeVar, Union, Callable, Tuple
from crimson.code_extractor import extract
from crimson.ast_dev_tool import safe_unparse, collect_nodes
from crimson.intelli_type import IntelliType
from crimson.intelli_type._replace_union import as_union
from inspect import getsource
import ast

T = TypeVar("T")


class Function_(IntelliType, Tuple[as_union, Callable, str, ast.FunctionDef], Generic[T]):
    """
    def func(arg1:int):
        return arg1


    It can be any of them among,

    func
    function_code = inspect.getsource(func)
    function_node = ast.parse(function_code)

    It is safe even if,
        - The function is not places at the first
        - There are many functions in it

    All the functions from auto-pydantic will deal with them flexibly.
    If there are many functions in it, the first function is the object this module uses.
    """


class Constructor_(IntelliType, str, Generic[T]):
    """
    It is the code lines of the constructor of the pydantic model.

    It allows you to use the model in the same structure where you use the function.

    function:
        def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs, ) -> str:
            return "bye"

    constructor: str
        def __init__(self, arg1: int, *args: Tuple[int, int], arg2: str='hi', arg3: int=1, **kwargs):
            super().__init__(arg1=arg1, args=args, arg2=arg2, arg3=arg3, kwargs=kwargs)

    """


class InputProps_(IntelliType, str, Generic[T]):
    """
    It is the code lines of the InputProps model for the target function's input parameters.

    function:
        def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs, ) -> str:
            return "bye"

    input_props: str
        class Func2InputProps(BaseModel):
            arg1: int = Field(...)
            args: Tuple[int, int] = Field(default=())
            arg2: str = Field(default="'hi'")
            arg3: int = Field(default='1')
            kwargs: Any = Field(default={})

            \{optional_constructor\}

    """


class OutputProps_(IntelliType, str, Generic[T]):
    """
    It is the code lines of the OutputProps model for the target function's return annotation.

    function:
        def func2(arg1: int, *args: Tuple[int, int], arg2: str = "hi", arg3: int = 1, **kwargs, ) -> str:
            return "bye"

    output_props: str
        class Func2OutputProps(BaseModel):
            return: str
    """


def generate_constructor(
    function: Function_[Union[Callable, str, ast.FunctionDef]], indent: int = 4
) -> Constructor_[str]:
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
