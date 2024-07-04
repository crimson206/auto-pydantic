from .generator import generate_constructor, generate_output_props, generate_input_props
from .generator_model import generate_inputprops_model
from .validator import validate
from .beta.test_loader import _extract_zip_to_dir, _create_zip_from_dir
from pathlib import Path


def _load_test_zip():
    test_dir = "../../test"
    _create_zip_from_dir(test_dir, Path(__file__).parent, 'test.zip', includes=['.py'], excludes=['__pycache__', '.pytest_cache'])


def extract_tests(out_dir):
    _extract_zip_to_dir(Path(__file__).parent / 'test.zip', out_dir)
