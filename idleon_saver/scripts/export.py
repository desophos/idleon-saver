import csv
import json
import logging
from abc import ABC, abstractmethod
from argparse import Namespace
from itertools import chain, repeat, starmap
from math import floor
from pathlib import Path
from string import ascii_lowercase
from typing import Any, Iterator, Optional, Tuple

from idleon_saver.data import (
    Bags,
    bag_maps,
    card_reqs,
    cog_boosts,
    cog_datas_map,
    cog_type_map,
    constellation_names,
    idleon_data,
    pouch_names,
    pouch_sizes,
    skill_names,
    stamp_names,
    starsign_ids,
    starsign_names,
    statues,
    vial_names,
    wiki_data,
)
from idleon_saver.utility import (
    Args,
    Formats,
    Sources,
    friendly_name,
    from_keys_in,
    get_args,
    zip_from_iterable,
)

logger = logging.getLogger(__name__)


def get_baseclass(which: int) -> int:
    if which in range(1, 5 + 1):
        # special case for beginner because it has only 4 subclasses
        return 1

    for base in [7, 19, 31]:  # warrior, archer, mage
        # each has 6 subclasses (unreleased but still in ClassNames)
        if which in range(base, base + 6 + 1):
            return base

    raise ValueError(f"Class {which} does not exist")


def get_classname(which: int) -> str:
    return idleon_data["classNames"][str(which)]


def get_starsign_from_index(i: int) -> str:
    return starsign_ids[starsign_names[i]]


def parse_player_starsigns(starsign_codes: str) -> dict[str, bool]:
    starsigns = []
    for k in starsign_codes.strip(",_").split(","):
        try:
            starsigns.append(get_starsign_from_index(int(k)))
        except ValueError:
            pass  # Malformed key ("" or "_")
        except KeyError as e:
            logger.exception(f"Couldn't parse starsign index {k}", exc_info=e)
    return dict.fromkeys(starsigns, True)


def get_cardtier(name: str, level: int) -> int:
    req = card_reqs[name]
    if level == 0:
        return 0
    elif level >= req * 9:
        return 4
    elif level >= req * 4:
        return 3
    elif level >= req:
        return 2
    else:
        return 1


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


def get_empties(cogs: list[str]) -> list[dict[str, int]]:
    if len(cogs) < 96:
        raise ValueError(
            "cog list must contain at least 96 entries to cover the whole cog board; "
            f"{len(cogs)} isn't enough"
        )

    empties: list[dict[str, int]] = []
    # The cog board is 8 rows by 12 columns = 96 spaces.
    for y in range(8):
        for x in range(12):
            i = y * 12 + x
            # Ignore occupied spaces.
            if cogs[i] == "Blank":
                empties.append({"empties_x": x, "empties_y": y})

    return empties


def get_cog_type(name: str) -> Optional[str]:
    # Check simple special cases.
    if name == "Blank":
        return None
    elif name.startswith("Player_"):
        return "Character"
    elif name == "CogY":
        return "Yang_Cog"
    elif name.startswith("CogZ"):
        return "Omni_Cog"

    # Check each type of directional cog.
    for direction, cog_type in cog_type_map.items():
        if name.endswith(direction):
            return f"{cog_type}_Cog"

    # If the name didn't match any special cases, it's just a regular cog.
    return "Cog"


def get_cog_data(cog: dict[str, Any], name: str) -> Optional[dict[str, Any]]:
    data = {}

    cog_type = get_cog_type(name)
    if cog_type is None:
        return None

    data["cog type"] = cog_type
    data["name"] = name.removeprefix("Player_") if cog_type == "Character" else ""

    for key, field in cog_datas_map.items():
        try:
            # Boosts are stored as percentages, so convert them to multipliers.
            data[field] = cog[key] / 100 if key in cog_boosts else cog[key]
        except KeyError:
            # Cogs only have keys for whatever bonuses they have,
            # but we need to fill in the missing fields for DictWriter.
            data[field] = ""

    return data


class Exporter(ABC):
    def __init__(self, savedata: dict) -> None:
        self.savedata = savedata

        self.classes: list[int] = self.all_players("CharacterClass")
        self.skill_levels: list[list[int]] = self.all_players("Lv0")
        self.statue_levels: list[list[list]] = self.all_players("StatueLevels")
        self.bags_used: list[list[str]] = [
            bags.keys() for bags in self.all_players("InvBagsUsed")
        ]  # Values are just the number of slots granted by the bag, so ignore them
        self.carrycaps: list[dict[str, int]] = self.all_players("MaxCarryCap")

        # Abstract attributes defined by subclasses
        self.names: list[str]
        self.stats: list[list[int]]
        self.cauldron: list[list[int]]
        self.starsigns_unlocked: dict[str, int]
        self.starsigns_prog: list[tuple[str, int]]
        self.starsigns_equipped: list[str]
        self.cards: dict[str, int]
        self.stamp_levels: list[list[int]]
        self.statues_golden: list[int]
        self.cog_map: list[dict[str, Any]]
        self.cog_order: list[str]

    @abstractmethod
    def all_players(self, key: str) -> list:
        raise NotImplementedError

    def export(self, fmt: Formats, workdir: Path):
        if fmt == Formats.IC:
            self.save_idleon_companion(workdir)
        elif fmt == Formats.COG:
            self.save_cogstruction(workdir)
        else:
            raise ValueError(
                f"Format must be idleon_companion or cogstruction, not {fmt}"
            )

    def save_idleon_companion(self, workdir: Path):
        outfile = workdir / "idleon_companion.json"

        with open(outfile, "w", encoding="utf-8") as file:
            json.dump(self.to_idleon_companion(), file)

        logger.info(f"Wrote file: {outfile}")

    def to_idleon_companion(self) -> dict:
        return {
            "alchemy": self.get_alchemy(),
            "starSigns": self.get_starsigns(),
            "cards": self.get_cards(),
            "stamps": {name: level for name, level in self.get_stamps() if level > 0},
            "statues": self.get_statues(),
            "checklist": self.get_checklist(),
            "chars": self.get_chars(),
        }

    def save_cogstruction(self, workdir: Path):
        data = self.to_cogstruction()

        for which in ["cog_datas", "empties_datas"]:
            outfile = workdir / f"{which}.csv"

            with open(outfile, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data[which][0].keys())

                writer.writeheader()
                for row in data[which]:
                    writer.writerow(row)

            logger.info(f"Wrote file: {outfile}")

    def to_cogstruction(self) -> dict[str, Any]:
        return {
            "cog_datas": list(
                filter(
                    None,
                    starmap(
                        get_cog_data,
                        zip(self.cog_map, self.cog_order),
                    ),
                )
            ),  # Filter to ignore blank cogs.
            "empties_datas": get_empties(self.cog_order),
        }

    def char_map(self) -> dict[str, str]:
        return dict(zip(self.names, "_" + ascii_lowercase))

    def get_alchemy(self):
        # Get possibly empty alchemy data.
        try:
            upgrades = self.cauldron[:4]
        except IndexError:
            upgrades = repeat([])
        try:
            vial_levels = self.cauldron[4]
        except IndexError:
            vial_levels = []

        return {
            "upgrades": dict(zip(("Orange", "Green", "Purple", "Yellow"), upgrades)),
            "vials": {
                friendly_name(name): level
                for name, level in zip(vial_names, vial_levels)
                if level > 0
            },
        }

    def get_starsigns(self) -> dict[str, bool]:
        return {
            starsign_ids[name]: bool(unlocked)
            for name, unlocked in self.starsigns_unlocked.items()
        }

    def get_cards(self) -> dict[str, int]:
        return {
            wiki_data["EnemyDetails"][name]["Name"]: get_cardtier(name, level)
            for name, level in self.cards.items()
            if level > 0
        }

    def get_stamps(self) -> Iterator[Tuple[str, int]]:
        return chain.from_iterable(
            zip(stamps, levels)
            for stamps, levels in zip(stamp_names, self.stamp_levels)
        )

    def get_statues(self) -> dict:
        """Explanation of zip magic:
        0. statue_levels:
           list of characters, each with a list of statues, each with (level, progress)
        1. zip_from_iterable(_):
           list of statues, each with a list of characters, each with (level, progress)
        2. map(zip_from_iterable, _):
           list of statues, each with (list of levels, list of progresses)
        3. zip_from_iterable(_):
           ([list of statues, each with a list of levels], [list of statues, each with a list of progresses])
        4. for lvls, progs in zip(*_):
           iterates over statues, unpacking each into a list of levels and list of progresses
        """
        return {
            name: {
                "golden": bool(gold),
                "level": max(lvls),
                "progress": floor(max(progs)),
            }
            for name, gold, lvls, progs in zip(
                statues,
                self.statues_golden,
                *zip_from_iterable(
                    map(zip_from_iterable, zip_from_iterable(self.statue_levels))
                ),
            )
        }

    def get_checklist(self) -> dict[str, bool]:
        return (
            # DeepSource error due to old python/mypy version? skipcq: TYP-052
            from_keys_in(
                bag_maps[Bags.GEM],
                self.bags_used[0],
                True,
            )
            | from_keys_in(
                bag_maps[Bags.STORAGE], self.savedata["InvStorageUsed"].keys(), True
            )
            | {name: True for name, level in self.get_stamps() if level > 0}
        )

    def get_player_constellations(self, charname: str) -> dict[str, bool]:
        return {
            constellation_names[i]: True
            for i, (chars, completed) in enumerate(self.starsigns_prog)
            if self.char_map()[charname] in (chars or "")  # chars can be null
        }

    def build_char(
        self,
        name: str,
        klass: int,
        stats: list[int],
        starsigns: str,
        skills: list[int],
        bags: list[str],
        carrycaps: dict[str, int],
    ):
        try:
            level = stats[4]
        except IndexError:
            # Characters that have never been played have placeholder stats
            # that don't include level, so make up a placeholder level.
            level = 0

        return {
            "name": name,
            "class": get_classname(klass),
            "level": level,
            "constellations": self.get_player_constellations(name),
            "starSigns": parse_player_starsigns(starsigns),
            "skills": dict(list(zip(skill_names, skills))[1:]),
            # DeepSource error due to old python/mypy version? skipcq: TYP-052
            "items": from_keys_in(bag_maps[Bags.INV], bags, True)
            | get_pouches(carrycaps),
        }

    def get_chars(self) -> list[dict]:
        return list(
            starmap(
                self.build_char,
                zip(
                    self.names,
                    self.classes,
                    self.stats,
                    self.starsigns_equipped,
                    self.skill_levels,
                    self.bags_used,
                    self.carrycaps,
                ),
            )
        )


class LocalExporter(Exporter):
    def __init__(self, savedata: dict) -> None:
        super().__init__(savedata)
        self.names = savedata["GetPlayersUsernames"]
        self.stats = [pv["StatList"] for pv in self.all_players("PersonalValuesMap")]
        self.starsigns_equipped = [
            pv["StarSign"] for pv in self.all_players("PersonalValuesMap")
        ]
        self.starsigns_unlocked = savedata["StarSignsUnlocked"]
        self.starsigns_prog = savedata["StarSignProg"]
        self.cauldron = savedata["CauldronInfo"]
        self.cards = savedata["Cards"][0]
        self.stamp_levels = savedata["StampLevel"]
        self.statues_golden = savedata["StatueG"]
        self.cog_map = savedata["CogMap"]
        self.cog_order = savedata["CogOrder"]

    def all_players(self, key: str) -> list:
        return [player[key] for player in self.savedata["PlayerDATABASE"].values()]


class FirebaseExporter(Exporter):
    def __init__(self, savedata: dict) -> None:
        super().__init__(savedata)
        self.names = savedata["PlayerNames"]
        self.stats = self.all_players("PVStatList")
        self.starsigns_equipped = self.all_players("PVtStarSign")
        self.starsigns_unlocked = savedata["StarSg"]
        self.starsigns_prog = savedata["SSprog"]
        self.cauldron = list(map(self.parse_pseudoarray, savedata["CauldronInfo"]))
        self.cards = savedata["Cards0"]
        self.stamp_levels = list(map(self.parse_pseudoarray, savedata["StampLv"]))
        self.statues_golden = savedata["StuG"]
        self.cog_order = savedata["CogO"]
        self.cog_map = self.parse_cog_map(savedata["CogM"])

    @staticmethod
    def parse_pseudoarray(obj: dict) -> list:
        if "length" not in obj:
            raise ValueError(f"Object has no `length` key: {obj}")
        return [v for k, v in obj.items() if k != "length"]

    def all_players(self, key: str) -> list:
        return [v for k, v in sorted(self.savedata.items()) if k.startswith(key)]

    def parse_cog_map(self, cog_map: dict[str, dict]) -> list[dict]:
        new_cogs = []
        for i in range(len(self.cog_order)):
            try:
                new_cogs.append(cog_map[str(i)])
            except KeyError:
                new_cogs.append({})
        return new_cogs


exporters = {
    Sources.LOCAL: LocalExporter,
    Sources.FIREBASE: FirebaseExporter,
}


def main(args: Namespace):
    infile = args.workdir / (args.infile or "decoded.json")
    with open(infile, encoding="utf-8") as file:
        data = json.load(file)
    exporters[args.source](data).export(args.to, args.workdir)


if __name__ == "__main__":
    main(get_args(Args.WORKDIR, Args.INFILE, Args.TO, Args.SOURCE))
