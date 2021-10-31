import json
import logging
from argparse import Namespace

from idleon_saver.ldb import ldb_args

logger = logging.getLogger(__name__)

WHITELIST = [
    "PlayerDATABASE",
    "GetPlayersUsernames",
    "CauldronInfo",
    "StarSignsUnlocked",
    "Cards",
    "StampLevel",
    "StatueG",
    "InvStorageUsed",
    "StarSignProg",
    "CogOrder",
    "CogMap",
]

CHAR_WHITELIST = [
    "CharacterClass",
    "PersonalValuesMap",
    "Lv0",
    "InvBagsUsed",
    "MaxCarryCap",
    "StatueLevels",
]


def main(args: Namespace):
    infile = args.workdir / (args.infile or "decoded.json")

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    data = {k: v for k, v in data.items() if k in WHITELIST}
    data["PlayerDATABASE"] = {
        name: {k: v for k, v in val.items() if k in CHAR_WHITELIST}
        for name, val in data["PlayerDATABASE"].items()
    }

    outfile = args.workdir / (args.outfile or "trimmed.json")
    with open(outfile, "w", encoding="ascii") as file:
        json.dump(data, file)

    logger.info(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
