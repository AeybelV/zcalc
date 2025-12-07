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

    materials = stackup.parse_materials(test_data["materials"])

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


def test_load_bad_materials():
    """
    Tests parse_materials(): when it takes in a invalid materials section
    """

    # ========== Invalid Mapping for a Material ==========
    test_data1 = {
        "materials": {
            "FR4_CORE": None,
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data1["materials"])

    assert "must be a mapping" in str(excinfo.value).lower()

    # ========== Missing required property ==========

    test_data2 = {
        "materials": {
            "FR4_CORE": {"er": 4.4},
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data2["materials"])

    assert "missing required field: 'kind'" in str(excinfo.value).lower()

    # ========== Dielectric constant typing ==========

    test_data3 = {
        "materials": {
            "FR4_CORE": {"kind": "dielectric", "er": "foo"},
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data3["materials"])

    assert "dielectric constant 'er' must be float" in str(excinfo.value).lower()
