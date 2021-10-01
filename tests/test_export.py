import pytest
from scripts.export import get_cog_type, get_empties, save_cogstruction, to_cogstruction

from data import cog_type_map


def test_get_empties_error():
    with pytest.raises(AssertionError):
        get_empties([])


def test_get_empties(jsonsave):
    cogs = jsonsave["CogOrder"]
    empties = get_empties(cogs)

    assert len(empties) == cogs[:96].count("Blank")
    for slot in empties:
        assert slot.keys() == set(("empties_x", "empties_y"))
        assert slot["empties_x"] in range(12)
        assert slot["empties_y"] in range(8)


@pytest.mark.parametrize(
    ("name", "cog_type"),
    [
        ("Blank", None),
        ("Player_", "Character"),
        ("Player_XYZ", "Character"),
        ("CogY", "Yang_Cog"),
        ("CogZ", "Omni_Cog"),
        ("Cog1A00", "Cog"),
        ("XYZ", "Cog"),
        ("_", "Cog"),
    ],
)
def test_get_cog_type(name, cog_type):
    assert cog_type == get_cog_type(name)


@pytest.mark.parametrize(("direction", "cog_type"), cog_type_map.items())
def test_get_cog_type_directions(direction, cog_type):
    assert f"{cog_type}_Cog" == get_cog_type(f"CogABC{direction}")
