import csv
import json
import logging
from argparse import ArgumentParser, Namespace
from enum import Enum
from itertools import chain, starmap
from math import floor
from pathlib import Path
from string import ascii_lowercase
from typing import Any, Iterator, Tuple, Union

from data import (
    Bags,
    bag_maps,
    card_bases,
    card_names,
    class_names,
    cog_boosts,
    cog_datas_map,
    cog_type_map,
    constellation_names,
    pouch_names,
    pouch_sizes,
    skill_names,
    stamp_names,
    starsign_ids,
    starsign_names,
    statue_names,
    vial_names,
)
from idleon_saver.ldb import ldb_args
from idleon_saver.utility import from_keys_in, zip_from_iterable

logger = logging.getLogger(__name__)


class Formats(Enum):
    IC = "idleon_companion"
    COG = "cogstruction"

    @staticmethod
    def lookup(key: str):
        for member in Formats.__members__.values():
            if member.value == key:
                return member


def friendly_name(s: str) -> str:
    return s.replace("_", " ").title()


def char_map(data: dict) -> dict[str, str]:
    return dict(zip(data["GetPlayersUsernames"], "_" + ascii_lowercase))


def get_baseclass(which: int) -> int:
    if 1 <= which and which <= 5:
        # special case for beginner because it has only 4 subclasses
        return 1
    else:
        for base in [7, 19, 31]:  # warrior, archer, mage
            # each has 6 subclasses (unreleased but still in ClassNames)
            if base <= which and which <= base + 6:
                return base
    raise ValueError(f"Class {which} does not exist")


def get_classname(which: int) -> str:
    return friendly_name(class_names[which])


def get_alchemy(data: dict) -> dict[str, dict]:
    return {
        "upgrades": dict(
            zip(("Orange", "Green", "Purple", "Yellow"), data["CauldronInfo"][:4])
        ),
        "vials": {
            friendly_name(name): level
            for name, level in zip(vial_names, data["CauldronInfo"][4])
            if level > 0
        },
    }


def get_starsign_from_index(i: int) -> str:
    return starsign_ids[starsign_names[i]]


def get_starsigns(data: dict) -> dict[str, bool]:
    return {
        starsign_ids[name]: bool(unlocked)
        for name, unlocked in data["StarSignsUnlocked"].items()
    }


def get_cardtier(name: str, level: int) -> int:
    base = card_bases[name]
    if level == 0:
        return 0
    elif level >= base * 9:
        return 4
    elif level >= base * 4:
        return 3
    elif level >= base:
        return 2
    else:
        return 1


def get_cards(data: dict) -> dict[str, int]:
    return {
        card_names[name]: get_cardtier(name, level)
        for name, level in data["Cards"][0].items()
        if level > 0
    }


def get_stamps(data: dict) -> Iterator[Tuple[str, int]]:
    return zip(stamp_names.values(), chain(*data["StampLevel"]))


def get_statues(data: dict) -> dict:
    return {
        name: {
            "golden": bool(gold),
            "level": max(lvls),
            "progress": floor(max(progs)),
        }
        for name, gold, lvls, progs in zip(
            statue_names,
            data["StatueG"],
            *[
                [
                    [statue[i] for statue in statues]
                    for statues in zip_from_iterable(
                        char["StatueLevels"] for char in data["PlayerDATABASE"].values()
                    )
                ]
                for i in range(2)
            ],
        )
    }


def get_checklist(data: dict) -> dict[str, bool]:
    return (
        from_keys_in(
            bag_maps[Bags.GEM],
            list(data["PlayerDATABASE"].values())[0]["InvBagsUsed"],
            True,
        )
        | from_keys_in(bag_maps[Bags.STORAGE], data["InvStorageUsed"].keys(), True)
        | {name: True for name, level in get_stamps(data) if level > 0}
    )


def get_pouchsize(itemtype: str, stacksize: int) -> str:
    return (
        "Mini"
        if stacksize == 25 and itemtype == "bCraft"
        else "Miniscule"
        if stacksize == 25 and itemtype == "Foods"
        else pouch_sizes[stacksize]
    )


def get_pouches(carrycaps: dict[str, int]) -> dict[str, bool]:
    return {
        " ".join(
            [
                get_pouchsize(itemtype, stacksize),
                pouch_names[itemtype],
                "Pouch",
            ]
        ): True
        for itemtype, stacksize in carrycaps.items()
        if stacksize > 10
    }


def get_chars(data: dict) -> list[dict]:
    return [
        {
            "name": charname,
            "class": get_classname(chardata["CharacterClass"]),
            "level": chardata["PersonalValuesMap"]["StatList"][4],
            "constellations": {
                constellation_names[i]: True
                for i, (chars, completed) in enumerate(data["StarSignProg"])
                if char_map(data)[charname] in chars
            },
            "starSigns": {
                get_starsign_from_index(int(k)): True
                for k in chardata["PersonalValuesMap"]["StarSign"]
                .strip(",_")
                .split(",")
            },
            "skills": dict(list(zip(skill_names, chardata["Lv0"]))[1:]),
            "items": from_keys_in(
                bag_maps[Bags.INV], chardata["InvBagsUsed"].keys(), True
            )
            | get_pouches(chardata["MaxCarryCap"]),
        }
        for charname, chardata in data["PlayerDATABASE"].items()
    ]


def to_idleon_companion(raw: dict) -> dict:
    return {
        "alchemy": get_alchemy(raw),
        "starSigns": get_starsigns(raw),
        "cards": get_cards(raw),
        "stamps": {name: level for name, level in get_stamps(raw) if level > 0},
        "statues": get_statues(raw),
        "checklist": get_checklist(raw),
        "chars": get_chars(raw),
    }


def save_idleon_companion(workdir: Path, data: dict):
    outfile = workdir / "idleon_companion.json"

    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(data, file)

    logger.info(f"Wrote file: {outfile}")


def get_empties(raw: dict) -> list[dict[str, int]]:
    empties = []

    for y in range(8):
        for x in range(12):
            i = y * 12 + x
            if i >= 96:
                break
            elif raw["CogOrder"][i] == "Blank":
                empties.append({"empties_x": x, "empties_y": y})

    return empties


def get_cog_data(cog: dict[str, Any], name: str) -> Union[None, dict[str, Any]]:
    data = {"cog type": "Cog", "name": ""}

    if name == "Blank":
        return None
    elif name.startswith("Player_"):
        data["cog type"] = "Character"
        data["name"] = name.removeprefix("Player_")
    elif name == "CogY":
        data["cog type"] = "Yang_Cog"
    elif name.startswith("CogZ"):
        data["cog type"] = "Omni_Cog"
    else:
        for abbr, cog_type in cog_type_map.items():
            if name.endswith(abbr):
                data["cog type"] = f"{cog_type}_Cog"
                break

    for abbr, field in cog_datas_map.items():
        try:
            data[field] = cog[abbr] / 100 if abbr in cog_boosts else cog[abbr]
        except KeyError:
            data[field] = ""

    return data


def to_cogstruction(raw: dict) -> dict[str, Any]:
    return {
        "cog_datas": filter(
            None, starmap(get_cog_data, zip(raw["CogMap"], raw["CogOrder"]))
        ),
        "empties_datas": get_empties(raw),
    }


def save_cogstruction(workdir: Path, data: dict):
    for which in ["cog_datas", "empties_datas"]:
        outfile = workdir / f"{which}.csv"

        with open(outfile, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=data[which][0].keys())

            writer.writeheader()
            for row in data[which]:
                writer.writerow(row)

        logger.info(f"Wrote file: {outfile}")


def main(args: Namespace):
    export_parsers = {Formats.IC: to_idleon_companion, Formats.COG: to_cogstruction}
    export_savers = {Formats.IC: save_idleon_companion, Formats.COG: save_cogstruction}

    infile = args.workdir / (args.infile or "decoded.json")
    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    parsed = export_parsers[args.to](data)
    export_savers[args.to](args.workdir, parsed)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--to",
        choices=[f for f in Formats],
        type=Formats.lookup,
        default=Formats.IC,
        help="format to parse save data into",
    )
    main(ldb_args(parser))
