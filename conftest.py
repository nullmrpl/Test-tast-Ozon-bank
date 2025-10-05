import pytest
import logging

from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def logger_setting():
    logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="session", autouse=False)
def file_path():
    test_file_dir = Path(__file__).parent
    return Path(test_file_dir, "all_data_about_superhero.json")