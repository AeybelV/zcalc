import pytest

import zcalc.stackup as stackup


def test_load_materials():
    """
    Tests parse_materials(): which takes in a YAML materials section and converts it
    to a mapping of the material name to its Material Properties
    """

    test_data = {
        "materials": {
            "FR4_CORE": {"kind": "dielectric", "er": 4.6},
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    materials = stackup.parse_materials(test_data)

    # ensure keys exist
    assert set(materials.keys()) == {"FR4_CORE", "FR4_PREPEG", "COPPER_STD"}

    # FR4 Core
    core = materials["FR4_CORE"]
    assert isinstance(core, stackup.Material)
    assert core.name == "FR4_CORE"
    assert core.kind == "dielectric"
    assert core.er == 4.6
    assert core.conductivity is None

    # FR4 Prepeg
    prepeg = materials["FR4_PREPEG"]
    assert isinstance(prepeg, stackup.Material)
    assert prepeg.name == "FR4_PREPEG"
    assert prepeg.kind == "dielectric"
    assert prepeg.er == 4.4
    assert prepeg.conductivity is None

    # Copper
    cu = materials["COPPER_STD"]
    assert isinstance(cu, stackup.Material)
    assert cu.name == "COPPER_STD"
    assert cu.kind == "copper"
