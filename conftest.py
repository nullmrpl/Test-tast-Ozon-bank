import pytest
import logging

@pytest.fixture(scope="session", autouse=True)
def logger_setting():
    logging.getLogger("urllib3").setLevel(logging.WARNING)