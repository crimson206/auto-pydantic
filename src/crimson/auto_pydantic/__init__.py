from .generator import generate_constructor, generate_output_props, generate_input_props
from .validator import validate

import zipfile
import os


def extract_tests(destination):
    """
    ZIP 파일에서 test 폴더를 추출합니다.

    :param destination: test 폴더를 추출할 목적지 경로
    """
    package_dir = os.path.dirname(__file__)
    zip_path = os.path.join(package_dir, "test.zip")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(destination)
    print(f"Tests have been extracted to {destination}")
