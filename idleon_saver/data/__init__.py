import json
from enum import Enum
from itertools import chain, groupby
from operator import itemgetter, not_, truth
from typing import Callable, Mapping

from idleon_saver.utility import ROOT_DIR

idleon_data = {}
for path in ROOT_DIR.joinpath("idleon-data", "maps").iterdir():
    if path.suffix != ".json":
        continue
    with open(path, "r") as f:
        jsondata = json.load(f)
        # Every data file should have a comment, which we can ignore.
        try:
            del jsondata["__comment"]
        except KeyError:
            pass  # The file doesn't have a comment, which is fine.
        # If a data file has a top-level list, it's contained in the `data` field.
        idleon_data[path.stem] = jsondata.get("data", jsondata)

wiki_data = {}
for path in ROOT_DIR.joinpath("IdleonWikiBot", "exported", "repo").iterdir():
    if path.suffix != ".json":
        continue
    with open(path, "r") as f:
        wiki_data[path.stem.removesuffix("Repo")] = json.load(f)

skill_names = [
    "Character",
    "Mining",
    "Smithing",
    "Choppin'",
    "Fishing",
    "Alchemy",
    "Catching",
    "Trapping",
    "Construction",
    "Worship",
]

card_reqs = {name: vals["perTier"] for name, vals in wiki_data["Card"].items()}

vial_names = [
    name for name, vals in wiki_data["Bubble"].items() if vals["cauldron"] == "Vials"
]

stamps = [
    list(stamps)
    for _, stamps in groupby(
        filter(
            lambda stamp: stamp["typeGen"] == "aStamp",
            wiki_data["SpecificItem"].values(),
        ),
        itemgetter("Type"),
    )
]

stamp_names = [[stamp["displayName"] for stamp in group] for group in stamps]


class Bags(Enum):
    INV = "inventory"
    GEM = "gem_shop"
    STORAGE = "storage"


def get_bag_names(
    typeGen: str, gem: Callable[[bool], bool] = lambda _: True
) -> dict[str, str]:
    return {
        item["item"]["internalName"]: item["item"]["displayName"]
        for item in wiki_data["Item"].values()
        if item["item"]["typeGen"] == typeGen
        and item["sources"]  # unobtainable bags have null sources
        and gem(
            any(
                source["txtName"].lower() == "gem shop"
                for source in item["sources"].get("sources", [])
            )
        )
    }


def get_bag_index_to_name(bag_names: Mapping[str, str]) -> dict[str, str]:
    return {
        str(item["order"]): bag_names[item["bag"]]
        for item in wiki_data["StorageOrder"].values()
        if item["bag"] in bag_names
    }


bag_maps = {
    Bags.INV: get_bag_index_to_name(get_bag_names("aInventoryBag", not_)),
    Bags.GEM: get_bag_index_to_name(get_bag_names("aInventoryBag", truth)),
    Bags.STORAGE: get_bag_index_to_name(get_bag_names("aStorageChest")),
}

pouch_names = {
    "Mining": "Mining",
    "Chopping": "Choppin",
    "Foods": "Food",
    "bCraft": "Materials",
    "Fishing": "Fish",
    "Bugs": "Bug",
    "Critters": "Critter",
    "Souls": "Soul",
}

pouch_sizes = {
    25: "Miniature",
    50: "Cramped",
    100: "Small",
    250: "Average",
    500: "Sizable",
    1000: "Big",
    2000: "Large",
}

starsign_names = list(wiki_data["StarSigns"].keys())

starsign_ids = {
    "The_Book_Worm": "1",
    "The_Buff_Guy": "1a",
    "The_Fuzzy_Dice": "1b",
    "Flexo_Bendo": "2",
    "Dwarfo_Beardus": "3",
    "Hipster_Logger": "4",
    "Pie_Seas": "4a",
    "Miniature_Game": "4b",
    "Shoe_Fly": "4c",
    "Pack_Mule": "5",
    "Pirate_Booty": "6",
    "All_Rounder": "7",
    "Muscle_Man": "7a",
    "Fast_Frog": "7b",
    "Smart_Stooge": "7c",
    "Lucky_Larry": "7d",
    "Fatty_Doodoo": "8",
    "Robinhood": "9",
    "Blue_Hedgehog": "9a",
    "Ned_Kelly": "10",
    "The_Fallen_Titan": "10a",
    "Chronus_Cosmos": "CR",
    "Activelius": "11",
    "Gum_Drop": "11a",
    "Mount_Eaterest": "12",
    "Bob_Build_Guy": "13",
    "The_Big_Comatose": "14",
    "Sir_Savvy": "14a",
    "Silly_Snoozer": "15",
    "The_Big_Brain": "15a",
    "Grim_Reaper": "16",
    "The_Forsaken": "16a",
    "The_OG_Skiller": "17",
    "Mr_No_Sleep": "18",
    "All_Rounderi": "19",
    "Centaurii": "20",
    "Murmollio": "21",
    "Strandissi": "22",
    "Agitagi": "22a",
    "Wispommo": "23",
    "Lukiris": "23a",
    "Pokaminni": "24",
    "Gor_Bowzor": "25",
    "Hydron_Cosmos": "26",
    "Trapezoidburg": "26a",
    "Sawsaw_Salala": "27",
    "Preys_Bea": "27B",
    "Cullingo": "28",
    "Gum_Drop_Major": "28a",
    "Grim_Reaper_Major": "29",
    "Sir_Savvy_Major": "30",
    "The_Bulwark": "31",
    "Big_Brain_Major": "32",
    "The_Fiesty": "33",
    "The_Overachiever": "33a",
    "Comatose_Major": "34",
    "S._Snoozer_Major": "35",
}

constellation_names = list(
    chain.from_iterable([f"{c}-{i}" for i in range(1, 13)] for c in "ABC")
)

cog_datas_map = {
    "a": "build_rate",
    "c": "flaggy_rate",
    "d": "exp_mult",
    "b": "exp_rate",
    "e": "build_rate_boost",
    "g": "flaggy_rate_boost",
    "k": "flaggy_speed",
    "f": "exp_rate_boost",
}

cog_boosts = "defg"

cog_type_map = {
    "ad": "Plus",
    "di": "X",
    "up": "Up",  # guess
    "do": "Down",
    "ri": "Right",
    "le": "Left",
    "ro": "Row",  # guess
    "co": "Col",  # guess
}
