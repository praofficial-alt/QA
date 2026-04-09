import pytest

from utils.config import get_base_url


@pytest.fixture(scope="session")
def base_url() -> str:
    return get_base_url()
