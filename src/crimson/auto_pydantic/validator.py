from typing import Callable, Dict, Any, TypeVar, Generic
from crimson.auto_pydantic.generator import _generate_input_props_name
from crimson.auto_pydantic.generator_model import (
    generate_inputprops_model,
    _prepare_namespace,
    CurrentFrame_,
    Func_,
    _NameSpace_,
    _FuncName_,
)
from types import FrameType
from pydantic import BaseModel, Field
from crimson.intelli_type import IntelliType
import threading


_data_classes_lock = threading.Lock()
_data_classes = {}


T = TypeVar("T")


class Config(BaseModel):
    on: bool = Field(
        default=True,
        description="""If it is off(False), the validate function will pass.
I'd prefer to validate my functions during development, but turn off when I publish my packages.""",
    )


config = Config()


class Bool_:
    """
    Dummy of bool type.
    """


class Validated_(IntelliType[bool], Generic[T]):
    """
    It doesn't mean whether the validation was successful or not.
    It rather shows the validate function was conducted or just passed.
    """
    _annotation = bool


def validate(func: Func_[Callable], currentframe: CurrentFrame_[FrameType], *args: Any, **kwargs: Any) -> Validated_[bool]:
    if config.on is False:
        return False

    namespace = _prepare_namespace(currentframe, args, kwargs)
    func_name = _generate_input_props_name(func.__name__)
    InputProps = _get_or_create_input_props(func, currentframe, args, kwargs)
    namespace[func_name] = InputProps

    _execute_validation(func_name, namespace)
    return True


def _get_or_create_input_props(
    func: Func_[Callable], currentframe: CurrentFrame_[FrameType], *args: Any, **kwargs: Any
) -> None:
    with _data_classes_lock:
        if func not in _data_classes:
            _data_classes[func] = generate_inputprops_model(func, currentframe, args, kwargs)

    return _data_classes[func]


def _execute_validation(func_name: _FuncName_[str], namespace: _NameSpace_[Dict[str, Any]]) -> None:
    validation = f"\n{func_name}(*args, **kwargs)"
    exec(validation, namespace)
