import pytest


@pytest.fixture
def stencylsave():
    with open("tests/stencylsave.txt", "r") as f:
        return f.read()
