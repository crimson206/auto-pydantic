import pytest
from crimson.auto_pydantic.validator import validate, config
from inspect import currentframe, getsource


@pytest.fixture
def reset_config():
    original_config = config.on
    yield
    config.on = original_config


class A:
    pass


def simple_function(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"


def complex_function(arg1: int, arg2: int = 1, *args: tuple, kwarg1: str = "default", **kwargs) -> dict:
    return {}


def init_generic_function(arg1: A) -> int:
    validate(init_generic_function, currentframe(), arg1)
    return 1


def init_validate_function(arg1: int, arg2: str = "default") -> str:
    validate(init_validate_function, currentframe(), arg1, arg2="default")
    return f"{arg1} {arg2}"


def test_validate_simple_valid():
    # This should not raise any exception
    source = getsource(simple_function)
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


def test_validate_generic_function():
    a = A()
    init_generic_function(a)


def test_init_validate_function():
    init_validate_function(1, "string")


def test_validate_simple(reset_config):
    # Test when config is on
    config.on = True
    assert validate(simple_function, currentframe(), 1, "test") is True

    # Test when config is off
    config.on = False
    assert validate(simple_function, currentframe(), 1, "test") is False


def test_validate_in_function(reset_config):
    def wrapper_function(x: int, y: str) -> str:
        validated = validate(simple_function, currentframe(), x, y)
        return validated

    # Test when config is on
    config.on = True
    assert wrapper_function(1, "test") is True

    # Test when config is off
    config.on = False
    assert wrapper_function(1, "test") is False
