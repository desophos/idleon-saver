import json
from enum import Enum
from itertools import chain

from idleon_saver.utility import ROOT_DIR

gamedata = {}
for path in ROOT_DIR.joinpath("idleon-data", "maps").iterdir():
    if path.suffix != ".json":
        continue
    with open(path, "r") as f:
        jsondata = json.load(f)
        # Every data file should have a comment, which we can ignore.
        del jsondata["__comment"]
        # If a data file has a top-level list, it's contained in the `data` field.
        gamedata[path.stem] = jsondata.get("data", jsondata)

class_names = [
    "0",
    "BEGINNER",
    "JOURNEYMAN",
    "MAESTRO",
    "VIRTUOSO",
    "INFINILYTE",
    "RAGE_BASICS",
    "WARRIOR",
    "BARBARIAN",
    "SQUIRE",
    "BLOOD_BERSERKER",
    "DEATH_BRINGER",
    "DIVINE_KNIGHT",
    "ROYAL_GUARDIAN",
    "FILLER",
    "FILLER",
    "FILLER",
    "FILLER",
    "CALM_BASICS",
    "ARCHER",
    "BOWMAN",
    "HUNTER",
    "SIEGE_BREAKER",
    "MAYHEIM",
    "WIND_WALKER",
    "BEAST_MASTER",
    "FILLER",
    "FILLER",
    "FILLER",
    "FILLER",
    "SAVVY_BASICS",
    "MAGE",
    "WIZARD",
    "SHAMAN",
    "ELEMENTAL_SORCERER",
    "SPIRITUAL_MONK",
    "BUBONIC_CONJUROR",
    "ARCANE_CULTIST",
    "FILLER",
    "FILLER",
    "FILLER",
    "FILLER",
    "MINING",
    "SMITHING",
    "CHOPPING",
    "FISHING",
    "ALCHEMY",
    "BUG_CATCHING",
    "TRAPPING",
    "CONSTRUCTION",
    "WORSHIP",
]

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

statue_names = [
    "Power",
    "Speed",
    "Mining",
    "Feasty",
    "Health",
    "Kachow",
    "Lumberbob",
    "Thicc Skin",
    "Oceanman",
    "Ol Reliable",
    "Exp Book",
    "Anvil",
    "Cauldron",
    "Beholder",
    "Bullseye",
    "Box",
    "Twosoul",
    "EhExPee",
    "Seesaw",
]

card_reqs = {
    card["name"]: card["amountPerTier"]
    for card in chain.from_iterable(gamedata["cards"])
}

vial_names = [vial["name"] for vial in gamedata["alchemy"]["vials"]]


class Bags(Enum):
    INV = "inventory"
    GEM = "gem_shop"
    STORAGE = "storage"


bag_keys = {
    Bags.INV: {
        "0": "InvBag1",
        "1": "InvBag2",
        "2": "InvBag3",
        "3": "InvBag4",
        "4": "InvBag5",
        "5": "InvBag6",
        "6": "InvBag7",
        "7": "InvBag8",
        "8": "InvBag9",
        "9": "InvBag10",
        "10": "InvBag11",
        "11": "InvBag12",
        "12": "InvBag13",
        "13": "InvBag14",
        "14": "InvBag15",
        "15": "InvBag16",
        "16": "InvBag17",
        "17": "InvBag18",
        "18": "InvBag19",
        "19": "InvBag20",
        "100": "InvBag100",
        "101": "InvBag101",
        "110": "InvBag110",
        "102": "InvBag102",
        "103": "InvBag103",
        "109": "InvBag109",
        "104": "InvBag104",
        "105": "InvBag105",
        "106": "InvBag106",
        "107": "InvBag107",
        "108": "InvBag108",
    },
    Bags.GEM: {
        "20": "InvBag21",
        "21": "InvBag22",
        "22": "InvBag23",
        "23": "InvBag24",
        "24": "InvBag25",
        "25": "InvBag26",
    },
    Bags.STORAGE: {
        "0": "InvStorage1",
        "1": "InvStorage2",
        "2": "InvStorage3",
        "3": "InvStorage4",
        "4": "InvStorage5",
        "5": "InvStorage6",
        "6": "InvStorage7",
        "7": "InvStorage8",
        "8": "InvStorage9",
        "9": "InvStorage10",
        "10": "InvStorage11",
        "11": "InvStorage12",
        "12": "InvStorage13",
        "14": "InvStorage14",
        "13": "InvStorage15",
        "15": "InvStorage16",
        "16": "InvStorage17",
        "17": "InvStorage18",
        "18": "InvStorage19",
        "19": "InvStorage20",
        "20": "InvStorage21",
        "21": "InvStorage22",
        "22": "InvStorage23",
        "23": "InvStorage24",
        "24": "InvStorage25",
        "25": "InvStorage26",
        "26": "InvStorage27",
        "27": "InvStorage28",
        "28": "InvStorage29",
        "29": "InvStorage30",
        "30": "InvStorage31",
        "31": "InvStorage32",
        "32": "InvStorage33",
        "33": "InvStorage34",
        "34": "InvStorage35",
        "35": "InvStorage36",
        "36": "InvStorage37",
        "37": "InvStorage38",
        "38": "InvStorage39",
        "39": "InvStorage40",
        "40": "InvStorage41",
        "41": "InvStorage42",
        "100": "InvStorageF",
        "101": "Blank",
    },
}

bag_names = {
    Bags.INV: {
        "InvBag1": "Inventory Bag A",
        "InvBag2": "Inventory Bag B",
        "InvBag3": "Inventory Bag C",
        "InvBag4": "Inventory Bag D",
        "InvBag5": "Inventory Bag E",
        "InvBag6": "Inventory Bag F",
        "InvBag7": "Inventory Bag G",
        "InvBag8": "Inventory Bag H",
        "InvBag9": "Inventory Bag I",
        "InvBag100": "Snakeskinventory Bag",
        "InvBag101": "Totally Normal and not fake Bag",
        "InvBag102": "Blunderbag",
        "InvBag103": "Sandy Satchel",
        "InvBag104": "Bummo Bag",
        "InvBag105": "Capitalist Case",
        "InvBag106": "Wealthy Wallet",
        "InvBag107": "Prosperous Pouch",
        "InvBag108": "Sack of Success",
        "InvBag109": "Shivering Sack",
        "InvBag110": "Mamooth Hide Bag",
    },
    Bags.GEM: {
        "InvBag21": "Inventory Bag U",
        "InvBag22": "Inventory Bag V",
        "InvBag23": "Inventory Bag W",
        "InvBag24": "Inventory Bag X",
        "InvBag25": "Inventory Bag Y",
        "InvBag26": "Inventory Bag Z",
    },
    Bags.STORAGE: {
        "InvStorage1": "Storage Chest 1",
        "InvStorage2": "Storage Chest 2",
        "InvStorage3": "Storage Chest 3",
        "InvStorage4": "Storage Chest 4",
        "InvStorage5": "Storage Chest 5",
        "InvStorage6": "Storage Chest 6",
        "InvStorage7": "Storage Chest 7",
        "InvStorage8": "Storage Chest 8",
        "InvStorage9": "Storage Chest 9",
        "InvStorage10": "Storage Chest 10",
        "InvStorage11": "Storage Chest 11",
        "InvStorage12": "Storage Chest 12",
        "InvStorage13": "Storage Chest 13",
        "InvStorage14": "Storage Chest 14",
        "InvStorage15": "Storage Chest 15",
        "InvStorage16": "Storage Chest 16",
        "InvStorage17": "Storage Chest 17",
        "InvStorage18": "Storage Chest 18",
        "InvStorage19": "Storage Chest 19",
        "InvStorage20": "Storage Chest 20",
        "InvStorage21": "Storage Chest 21",
        "InvStorage31": "Storage Chest 90",
        "InvStorage32": "Storage Chest 91",
        "InvStorage33": "Storage Chest 92",
        "InvStorage34": "Storage Chest 93",
        "InvStorage35": "Storage Chest 94",
        "InvStorage36": "Storage Chest 95",
        "InvStorage37": "Storage Chest 96",
        "InvStorage38": "Storage Chest 97",
        "InvStorage39": "Storage Chest 98",
        "InvStorage40": "Storage Chest 99",
        "InvStorage41": "Storage Chest 99B",
        "InvStorage42": "Storage Chest 99C",
        "InvStorageF": "Dank Paypay Chest",
    },
}

bag_maps = {
    group: {
        k: bag_names[group][v]
        for k, v in bag_keys[group].items()
        if v in bag_names[group]
    }
    for group in bag_names
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

starsign_names = [
    "The_Buff_Guy",
    "Flexo_Bendo",
    "The_Book_Worm",
    "The_Fuzzy_Dice",
    "Dwarfo_Beardus",
    "Hipster_Logger",
    "Pie_Seas",
    "Shoe_Fly",
    "Blue_Hedgehog",
    "Gum_Drop",
    "Activelius",
    "Pack_Mule",
    "Ned_Kelly",
    "Robinhood",
    "Pirate_Booty",
    "Muscle_Man",
    "Fast_Frog",
    "Smart_Stooge",
    "Lucky_Larry",
    "Silly_Snoozer",
    "The_Big_Comatose",
    "Miniature_Game",
    "Mount_Eaterest",
    "Bob_Build_Guy",
    "The_Big_Brain",
    "The_OG_Skiller",
    "Grim_Reaper",
    "The_Fallen_Titan",
    "The_Forsaken",
    "Mr_No_Sleep",
    "Sir_Savvy",
    "All_Rounder",
    "Fatty_Doodoo",
    "Chronus_Cosmos",
]

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
}

constellation_names = list(
    chain.from_iterable([f"{c}-{i}" for i in range(1, 13)] for c in "AB")
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
