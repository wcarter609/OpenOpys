import pytest

from src.openopys import OpenOpys

@pytest.fixture
def default_openopys():
    return OpenOpys()

def test_create_default_openopys(default_openopys):
    assert isinstance(default_openopys, OpenOpys), ""