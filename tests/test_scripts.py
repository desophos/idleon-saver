import pytest
from idleon_save_editor.utility import chunk
from scripts import json2stencyl, ldb2stencyl, stencyl2json, stencyl2ldb


@pytest.mark.parametrize(
    "scripts", [(stencyl2json, json2stencyl), (stencyl2ldb, ldb2stencyl)]
)
def test_inversion(testargs, stencylsave, scripts):
    with open(testargs.workdir / "encoded.txt", "w") as file:
        file.write(stencylsave)

    for script in scripts:
        script.main(testargs)

    with open(testargs.workdir / "encoded.txt", "r") as file:
        assert chunk(stencylsave, 50) == chunk(file.read(), 50)
