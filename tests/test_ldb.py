from scripts import ldb2stencyl, stencyl2ldb


def test_inversion(testargs, stencylsave):
    with open(testargs.workdir / "encoded.txt", "w") as file:
        file.write(stencylsave)

    stencyl2ldb.main(testargs)
    ldb2stencyl.main(testargs)

    with open(testargs.workdir / "decoded.txt", "r") as file:
        assert stencylsave == file.read()
