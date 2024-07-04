from crimson.file_loader.utils import filter_paths
from pathlib import Path
import zipfile


def _create_zip_from_dir(input_dir: str, output_dir: str, zip_name: str = "output.zip", includes=[], excludes=[]) -> str:
    """
    주어진 디렉토리의 내용을 ZIP 파일로 만들어 지정된 출력 디렉토리에 저장합니다.

    :param input_dir: ZIP으로 만들 디렉토리의 경로
    :param output_dir: ZIP 파일을 저장할 디렉토리의 경로
    :param zip_name: 생성할 ZIP 파일의 이름 (기본값: "output.zip")
    :return: 생성된 ZIP 파일의 전체 경로
    """
    paths = filter_paths(input_dir, includes, excludes)
    output_path = Path(output_dir).resolve()

    output_path.mkdir(parents=True, exist_ok=True)

    zip_path = output_path / zip_name

    # ZIP 파일 생성
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in paths:
            zipf.write(path, arcname=Path(path).name)

    return str(zip_path)


def _extract_zip_to_dir(zip_path: str, output_dir: str) -> str:
    """
    주어진 ZIP 파일을 지정된 출력 디렉토리에 풉니다.

    :param zip_path: 압축 해제할 ZIP 파일의 경로
    :param output_dir: ZIP 파일의 내용을 풀어낼 디렉토리의 경로
    :return: ZIP 파일이 압축 해제된 디렉토리의 전체 경로
    """
    # ZIP 파일 경로와 출력 디렉토리 경로를 Path 객체로 변환
    zip_file = Path(zip_path).resolve()
    output_path = Path(output_dir).resolve()

    # 출력 디렉토리가 존재하지 않으면 생성
    output_path.mkdir(parents=True, exist_ok=True)

    # ZIP 파일 압축 해제
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_path)

    return str(output_path)
