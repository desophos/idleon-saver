from argparse import Namespace
from pathlib import Path

import pytest
from scripts.common import db_key, ldb


@pytest.fixture(autouse=True, scope="session")
def testargs(tmp_path_factory) -> Namespace:
    args = Namespace()
    args.workdir = tmp_path_factory.mktemp("work")
    args.ldb = tmp_path_factory.mktemp("ldb")
    # doesn't need to be a real directory
    # because it's only used for the database key
    args.idleon = Path("C:/Program Files (x86)")
    return args


@pytest.fixture(autouse=True, scope="session")
def testdb(testargs):
    with ldb(testargs.ldb, create_if_missing=True) as db:
        db.put(db_key(testargs.idleon), b"_placeholder")
        return db


@pytest.fixture(scope="session")
def stencylsave():
    with open("tests/data/stencylsave.txt", "r") as f:
        return f.read()
