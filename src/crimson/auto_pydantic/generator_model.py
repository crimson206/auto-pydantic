from typing import Callable, Dict, Any, TypeVar, Generic, Literal
import ast
from crimson.ast_dev_tool import collect_nodes
from crimson.auto_pydantic.generator import (
    generate_input_props,
    _generate_input_props_name,
    generate_output_props,
    _generate_output_props_name,
)
from inspect import getsource
from crimson.intelli_type import IntelliType
from types import FrameType
from pydantic import BaseModel


T = TypeVar("T")


class Func_(IntelliType[Callable], Generic[T]):
    """
    Any function you defined.

    def my_func(arg1: int, arg2: str) -> str:
        return f'{arg2} : {arg1}'

    my_func: Func_[Callable]
    """


class CurrentFrame_(IntelliType[FrameType], Generic[T]):
    """
    from inspect import currentframe

    currentframe() : CurrentFrame_[FrameType]

    """


class InputPropsModel_(BaseModel, Generic[T]):
    """
    The generated model using the inputprops string from 'generator'.
    """


class _NameSpace_(IntelliType[Dict[str, Any]], Generic[T]):
    """
    It contains variables to be used to generate inputprops, returnprops, and constructor
    """


class _FuncName_(IntelliType[str], Generic[T]):
    """
    It might be the literal name of a function.
    However, it must be Camel case in the real usage.

    def snake_case():
        ...

    func_name = SnakeCase
    """


class _FunctionNode_(IntelliType[ast.FunctionDef], Generic[T]):
    """
    The ast module uses it to extract the props of Func_[str].
    """


def generate_inputprops_model(
    func: Func_[Callable], currentframe: CurrentFrame_[FrameType], env: Dict[str, Any] = {}, *args: Any, **kwargs: Any
) -> BaseModel:
    namespace = _prepare_namespace(currentframe, args, kwargs)
    function_node = _get_function_node(func)
    func_name = _generate_input_props_name(func.__name__)

    if len(env) != 0:
        namespace.update(env)

    InputProps = _create_props(function_node, func_name, namespace, mode='input')
    return InputProps


def generate_outputprops_model(
    func: Func_[Callable], currentframe: CurrentFrame_[FrameType], env: Dict[str, Any] = {}, *args: Any, **kwargs: Any
) -> BaseModel:
    namespace = _prepare_namespace(currentframe, args, kwargs)
    function_node = _get_function_node(func)
    func_name = _generate_output_props_name(func.__name__)

    if len(env) != 0:
        namespace.update(env)

    OutputProps = _create_props(function_node, func_name, namespace, mode='output')
    return OutputProps


def _prepare_namespace(
    currentframe: CurrentFrame_[FrameType], args: tuple, kwargs: dict
) -> _NameSpace_[Dict[str, Any]]:
    """
    It imports
        - the environment where validate is called
        - *args and **kwargs from function props
        - from pydantic import BaseModel, Field
        - from typing import Any

    I forgot why we need currentframe() instead of using globals().
    However, when I write this, I tested with globals(), and it ended up with an error.
    If time allows, it would be nice to analyze the reason and document it.
    """
    namespace: _NameSpace_[Dict[str, Any]] = {}
    namespace.update(currentframe.f_globals.copy())
    namespace.update({"args": args, "kwargs": kwargs})
    exec("from pydantic import BaseModel, Field\nfrom typing import Any", namespace, namespace)
    return namespace


def _get_function_node(func: Func_[Callable]) -> _FunctionNode_[ast.FunctionDef]:
    func_source = getsource(func)
    return collect_nodes(func_source, ast.FunctionDef)[0]


def _create_props(
    function_node: _FunctionNode_[ast.FunctionDef],
    func_name: _FuncName_[str],
    namespace: _NameSpace_[Dict[str, Any]],
    mode: Literal["input", "output"],
) -> InputPropsModel_[BaseModel]:
    if mode == "input":
        model = generate_input_props(function_node)
    elif mode == "output":
        model = generate_output_props(function_node)

    model = (
        model
        + """\n    class Config:
        arbitrary_types_allowed = True"""
    )

    local_scope = {}

    # Load necessary modules.
    # To use the loaded modules, it must be updated to namespace

    exec(model, namespace, local_scope)
    return local_scope[func_name]
