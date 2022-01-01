import json
import logging
from argparse import Namespace

from idleon_saver.utility import Args, Sources, get_args

logger = logging.getLogger(__name__)


LOCAL_WHITELIST = [
    "GetPlayersUsernames",
    "PlayerDATABASE",
    "StarSignsUnlocked",
    "StarSignProg",
    "CauldronInfo",
    "Cards",
    "StampLevel",
    "InvStorageUsed",
    "StatueG",
    "CogOrder",
    "CogMap",
]

FIREBASE_WHITELIST = [
    "PlayerNames",
    "PVStatList",
    "PVtStarSign",
    "StarSg",
    "SSprog",
    "CauldronInfo",
    "Cards0",
    "StampLv",
    "InvStorageUsed",
    "StuG",
    "CogO",
    "CogM",
]

CHAR_WHITELIST = [
    "CharacterClass",
    "PersonalValuesMap",
    "Lv0",
    "InvBagsUsed",
    "MaxCarryCap",
    "StatueLevels",
]


def trim_local(data: dict) -> dict:
    data = {k: v for k, v in data.items() if k in LOCAL_WHITELIST}
    data["PlayerDATABASE"] = {
        name: {k: v for k, v in val.items() if k in CHAR_WHITELIST}
        for name, val in data["PlayerDATABASE"].items()
    }
    return data


def trim_firebase(data: dict) -> dict:
    return {
        k: v
        for k, v in data.items()
        if any(k.startswith(key) for key in FIREBASE_WHITELIST + CHAR_WHITELIST)
    }


trimmers = {Sources.LOCAL: trim_local, Sources.FIREBASE: trim_firebase}


def main(args: Namespace):
    infile = args.workdir / (args.infile or "decoded.json")

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    data = trimmers[args.source](data)

    outfile = args.workdir / (args.outfile or "trimmed.json")
    with open(outfile, "w", encoding="ascii") as file:
        json.dump(data, file)

    logger.info(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(get_args(Args.INFILE, Args.OUTFILE, Args.WORKDIR, Args.SOURCE))
