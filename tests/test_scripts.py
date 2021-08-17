import pytest
from idleon_saver.utility import chunk
from scripts.decode import ldb2stencyl, stencyl2json
from scripts.encode import json2stencyl, stencyl2ldb


@pytest.mark.parametrize(
    "scripts", [(stencyl2json, json2stencyl), (stencyl2ldb, ldb2stencyl)]
)
def test_inversion(testargs, stencylsave, scripts):
    with open(testargs.workdir / "encoded.txt", "w") as file:
        file.write(stencylsave)

    for f in scripts:
        f(testargs)

    with open(testargs.workdir / "encoded.txt", "r") as file:
        assert chunk(stencylsave, 50) == chunk(file.read(), 50)
