from crimson.auto_pydantic import validate
from inspect import currentframe
from pydantic import BaseModel, Field  # noqa: F401


class A:
    pass


def simple_func(arg1: int):
    validate(simple_func, currentframe(), arg1)


def generic_func(arg1: A):
    validate(generic_func, currentframe(), arg1)
