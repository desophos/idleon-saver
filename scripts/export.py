import json
from argparse import ArgumentParser, Namespace
from enum import Enum
from itertools import chain
from math import floor
from string import ascii_lowercase
from typing import Iterator, Tuple

from data import (
    bag_names,
    card_names,
    constellation_names,
    gem_bag_names,
    pouch_names,
    pouch_sizes,
    skill_names,
    stamp_names,
    statue_names,
    storage_names,
)
from idleon_saver.ldb import ldb_args
from idleon_saver.utility import from_keys_in, normalize_workfile, zip_from_iterable


class Formats(Enum):
    IC = "idleon_companion"
    COG = "cogstruction"


def map_bags(names: dict[str, str], capacities: list[list[str]]) -> dict[str, str]:
    return {key: names[name] for key, _, name in capacities if name in names}


def bag_map(data: dict) -> dict[str, str]:
    return map_bags(bag_names, data["CustomLists"]["PlayerCapacities"][0])


def gem_bag_map(data: dict) -> dict[str, str]:
    return map_bags(gem_bag_names, data["CustomLists"]["PlayerCapacities"][0])


def storage_map(data: dict) -> dict[str, str]:
    return map_bags(storage_names, data["CustomLists"]["PlayerCapacities"][1])


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


def get_classname(data: dict, which: int) -> str:
    return data["CustomLists"]["ClassNames"][which].replace("_", " ").title()


def get_alchemy(data: dict) -> dict[str, dict]:
    return {
        "upgrades": dict(
            zip(("Orange", "Green", "Purple", "Yellow"), data["CauldronInfo"][:4])
        ),
        "vials": {
            str(k): v for k, v in enumerate(data["CauldronInfo"][4], start=1) if v > 0
        },
    }


def get_starsigns(data: dict) -> dict[str, bool]:
    return {
        name.replace("_", " "): bool(unlocked)
        for name, unlocked in data["StarSignsUnlocked"].items()
    }


def get_card_bases(data: dict) -> dict[str, float]:
    return {
        name: float(base)
        for name, _, base, _, _ in chain(*data["CustomLists"]["CardStuff"])
    }


def get_cardtier(data: dict, name: str, level: int) -> int:
    base = get_card_bases(data)[name]
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
        card_names[name]: get_cardtier(data, name, level)
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
            gem_bag_map(data),
            list(data["PlayerDATABASE"].values())[0]["InvBagsUsed"],
            True,
        )
        | from_keys_in(storage_map(data), data["InvStorageUsed"].keys(), True)
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
            "class": get_classname(data, chardata["CharacterClass"]),
            "level": chardata["PersonalValuesMap"]["StatList"][4],
            "constellations": {
                constellation_names[i]: True
                for i, (chars, completed) in enumerate(data["StarSignProg"])
                if char_map(data)[charname] in chars
            },
            "starSigns": {
                k: True
                for k in chardata["PersonalValuesMap"]["StarSign"]
                .strip(",_")
                .split(",")
            },
            "skills": dict(list(zip(skill_names, chardata["Lv0"]))[1:]),
            "items": from_keys_in(bag_map(data), chardata["InvBagsUsed"].keys(), True)
            | get_pouches(chardata["MaxCarryCap"]),
        }
        for charname, chardata in data["PlayerDATABASE"].items()
    ]


def to_idleon_companion(raw: dict) -> dict:
    return {
        "version": raw["CustomLists"]["PatchNotesInfo"][-1][0].lstrip("V"),
        "alchemy": get_alchemy(raw),
        "starSigns": get_starsigns(raw),
        "cards": get_cards(raw),
        "stamps": {name: level for name, level in get_stamps(raw) if level > 0},
        "statues": get_statues(raw),
        "checklist": get_checklist(raw),
        "chars": get_chars(raw),
    }


def to_cogstruction(raw: dict) -> dict:
    raise NotImplementedError


def main(args: Namespace):
    export_fns = {Formats.IC: to_idleon_companion, Formats.COG: to_cogstruction}
    export_files = {Formats.IC: "idleon_companion.json", Formats.COG: "cog_datas.csv"}

    infile = normalize_workfile(args.workdir, "decoded_plain.json")
    workdir = infile.parent

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    parsed = export_fns[args.to](data)

    outfile = workdir / export_files[args.to]
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(parsed, file)

    print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--to",
        choices=[f.value for f in Formats],
        default=Formats.IC,
        help="format to parse save data into",
    )
    main(ldb_args(parser))
