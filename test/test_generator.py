import pytest
import ast
from crimson.auto_pydantic.generator import generate_input_props, generate_output_props, generate_constructor


def create_function_node(func_str):
    return ast.parse(func_str).body[0]


@pytest.fixture
def simple_function():
    return create_function_node(
        """
def simple_func(arg1: int, arg2: str = "default") -> str:
    return f"{arg1} {arg2}"
"""
    )


@pytest.fixture
def complex_function():
    return create_function_node(
        """
def complex_func(
    arg1: int,
    *args: tuple,
    kwarg1: str = "default",
    **kwargs
) -> dict:
    return {}
"""
    )


def test_generate_input_props_simple(simple_function):
    result = generate_input_props(simple_function)
    expected = """\
class SimpleFuncInputProps(BaseModel):
    arg1: int = Field(...)
    arg2: str = Field(default="'default'")

    def __init__(self, arg1: int, arg2: str='default'):
        super().__init__(arg1=arg1, arg2=arg2)"""
    assert result.strip() == expected.strip()


def test_generate_input_props_complex(complex_function):
    result = generate_input_props(complex_function)
    expected = r"""class ComplexFuncInputProps(BaseModel):
    arg1: int = Field(...)
    args: tuple = Field(default=())
    kwarg1: str = Field(default="'default'")
    kwargs: Any = Field(default={})

    def __init__(self, arg1: int, *args: tuple, kwarg1: str='default', **kwargs):
        super().__init__(arg1=arg1, args=args, kwarg1=kwarg1, kwargs=kwargs)"""
    assert result.strip() == expected.strip()


def test_generate_output_props_simple(simple_function):
    result = generate_output_props(simple_function)
    expected = """class SimpleFuncOutputProps(BaseModel):
    return: str"""
    assert result.strip() == expected.strip()


def test_generate_output_props_complex(complex_function):
    result = generate_output_props(complex_function)
    expected = """class ComplexFuncOutputProps(BaseModel):
    return: dict"""
    assert result.strip() == expected.strip()


def test_generate_constructor_simple(simple_function):
    result = generate_constructor(simple_function)
    expected = r"""def __init__(self, arg1: int, arg2: str='default'):
        super().__init__(arg1=arg1, arg2=arg2)"""
    assert result.strip() == expected.strip()


def test_generate_constructor_complex(complex_function):
    result = generate_constructor(complex_function)
    expected = r"""    def __init__(self, arg1: int, *args: tuple, kwarg1: str='default', **kwargs):
        super().__init__(arg1=arg1, args=args, kwarg1=kwarg1, kwargs=kwargs)"""
    assert result.strip() == expected.strip()
