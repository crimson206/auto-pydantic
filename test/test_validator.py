import pytest
from crimson.auto_pydantic.validator import validate
from inspect import currentframe
from pydantic import BaseModel, Field  # noqa: F401


def simple_function(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"


def complex_function(arg1: int, arg2: int = 1, *args: tuple, kwarg1: str = "default", **kwargs) -> dict:
    return {}


def test_validate_simple_valid():
    # This should not raise any exception
    validate(simple_function, currentframe(), arg1=1, arg2="test")


def test_validate_simple_invalid_type():
    with pytest.raises(Exception):
        validate(simple_function, currentframe(), "not an int", "test")


def test_validate_simple_missing_required():
    with pytest.raises(Exception):  # We're just checking if any exception is raised
        validate(simple_function)


def test_validate_complex_valid():

    # This should not raise any exception
    validate(complex_function, currentframe(), 1, 2, 3, kwarg1="test", extra="stuff")


def test_validate_complex_invalid_type():
    with pytest.raises(Exception):
        validate(complex_function, currentframe(), "not an int")


def test_validate_complex_extra_args():
    # This should not raise any exception, as extra args are allowed
    validate(complex_function, currentframe(), 1, 2, 3, 4, 5, kwarg1="test", extra="stuff")


def test_validate_with_default():
    # This should not raise any exception, as arg2 has a default value
    validate(simple_function, currentframe(), 1)


def test_validate_override_default():
    # This should not raise any exception
    validate(simple_function, currentframe(), 1, "override")


def test_validate_kwargs():
    # This should not raise any exception
    validate(complex_function, currentframe(), arg1=1, kwarg1="test", extra="stuff")


def test_validate_mixed_args_kwargs():
    # This should not raise any exception
    validate(complex_function, currentframe(), 1, 2, 3, kwarg1="test", extra="stuff")
