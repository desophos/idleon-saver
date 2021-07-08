from pathlib import Path, PurePath

literals = {
    "n": None,
    "z": 0,
    "k": "NaN",
    "m": "-inf",
    "p": "inf",
    "t": True,
    "f": False,
}


db_path = {
    "prod": Path.home().joinpath(
        "AppData", "Roaming", "legends-of-idleon", "Local Storage", "leveldb"
    ),
    "test": Path.home().joinpath("dev", "leveldb"),
}


def db_key(steam_path: str = "C:/Steam") -> bytes:
    path = PurePath(steam_path).as_posix()
    return (
        b"_file://\x00\x01/"
        + bytes(path, encoding="utf-8")
        + b"/steamapps/common/Legends%20of%20Idleon/resources/app.asar/distBuild/static/game/index.html:mySave"
    )
