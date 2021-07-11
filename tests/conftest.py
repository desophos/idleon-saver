import pytest


@pytest.fixture
def stencylsave():
    with open("tests/data/stencylsave.txt", "r") as f:
        return f.read()
