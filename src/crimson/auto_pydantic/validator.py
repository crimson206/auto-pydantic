from typing import Callable, Dict, Any
import ast
from crimson.ast_dev_tool import collect_nodes
from crimson.auto_pydantic.generator import generate_input_props, _generate_input_props_name
from inspect import getsource
import typing
import threading


_data_classes_lock = threading.Lock()
_data_classes = {}


def validate(func: Callable, currentframe, *args, **kwargs):
    namespace = _prepare_namespace(currentframe, args, kwargs)
    function_node = _get_function_node(func)
    func_name = _generate_input_props_name(func.__name__)

    InputProps = _get_or_create_input_props(func, function_node, func_name, namespace)
    namespace[func_name] = InputProps

    _execute_validation(func_name, namespace)


def _prepare_namespace(currentframe, args, kwargs) -> Dict[str, Any]:
    namespace = {}
    namespace.update(currentframe.f_globals.copy())
    namespace.update(_get_types())
    namespace.update({"args": args, "kwargs": kwargs})
    return namespace


def _get_function_node(func: Callable) -> ast.FunctionDef:
    func_source = getsource(func)
    return collect_nodes(func_source, ast.FunctionDef)[0]


def _get_or_create_input_props(
    func: Callable, function_node: ast.FunctionDef, func_name: str, namespace: Dict[str, Any]
):
    with _data_classes_lock:
        if func not in _data_classes:
            _data_classes[func] = _create_input_props(function_node, func_name, namespace)
    return _data_classes[func]


def _create_input_props(function_node: ast.FunctionDef, func_name: str, namespace: Dict[str, Any]):
    model = generate_input_props(function_node)

    local_scope = {}
    exec(model, namespace, local_scope)
    return local_scope[func_name]


def _execute_validation(func_name: str, namespace: Dict[str, Any]):
    validation = f"\n{func_name}(*args, **kwargs)"
    exec(validation, namespace)


def _get_types() -> Dict[str, Any]:
    return {"Any": typing.Any}
