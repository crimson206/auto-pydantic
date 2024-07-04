from example1 import simple_func, generic_func, A
import pytest


def test_simple_func():
    valid_arg = 1
    unvalid_arg = "String"

    simple_func(valid_arg)

    with pytest.raises(Exception):
        simple_func(unvalid_arg)


def test_generic_func():
    generic_instance = A()

    generic_func(generic_instance)
