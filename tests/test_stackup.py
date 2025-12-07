import pytest

import zcalc.stackup as stackup

# =============== Materials Parsing ===============


def test_parse_materials():
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


def test_parse_materials_malformed():
    """
    Tests parse_materials with a Invalid Mapping for a Material and checks that it raises
    the correct exception
    """

    test_data = {
        "materials": {
            "FR4_CORE": None,
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data["materials"])

    assert "must be a mapping" in str(excinfo.value).lower()


def test_parse_materials_missing_kind():
    """
    Tests parse_materials with a Missing Mapping for a Material and checks that it raises
    the correct exception
    """

    test_data = {
        "materials": {
            "FR4_CORE": {
                # "kind" ommited
                "er": 4.6
            }
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data["materials"])

    assert "missing required field: 'kind'" in str(excinfo.value).lower()


def test_parse_materials_invalid_kind():
    """
    Tests parse_materials with a Invalid Kind for a Material and checks that it raises
    the correct exception
    """

    test_data = {
        "materials": {
            "FR4_CORE": {
                "kind": 123,
            }
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data["materials"])

    assert "validation error" in str(excinfo.value).lower()


def test_load_invalid_er():
    """
    Tests parse_materials with a Invalid ER for a Material and checks that it raises
    the correct exception
    """

    test_data = {
        "materials": {
            "FR4_CORE": {"kind": "dielectric", "er": "foo"},
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    }

    with pytest.raises(stackup.InvalidMaterials) as excinfo:
        stackup.parse_materials(test_data["materials"])

    assert "input should be a valid number" in str(excinfo.value).lower()


# =============== Layers Parsing ===============


def _make_materials_for_layers():
    return stackup.parse_materials(
        {
            "FR4_CORE": {"kind": "dielectric", "er": 4.6},
            "FR4_PREPEG": {"kind": "dielectric", "er": 4.4},
            "COPPER_STD": {"kind": "copper"},
        }
    )


def test_parse_layers_basic_indices_and_thickness():
    """
    Tests parse_layers with a valid layer and materials
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "copper",
            "material": "COPPER_STD",
            "thickness_um": 35,
        },
        {
            "name": "CORE",
            "type": "dielectric",
            "material": "FR4_CORE",
            "thickness_um": 800,
        },
        {
            "name": "L2_BOT",
            "type": "copper",
            "material": "COPPER_STD",
            "thickness_um": 35,
        },
    ]

    layers = stackup.parse_layers(layers_section, materials)

    assert len(layers) == 3

    l1 = layers[0]
    core = layers[1]
    l2 = layers[2]

    # Indices should match order in the list
    assert l1.index == 0
    assert core.index == 1
    assert l2.index == 2

    # Types & thickness
    assert l1.name == "L1_TOP"
    assert l1.type == stackup.LayerType.COPPER
    assert l1.thickness_um == pytest.approx(35.0)
    assert l1.material_name == "COPPER_STD"

    assert core.name == "CORE"
    assert core.type == stackup.LayerType.DIELECTRIC
    assert core.thickness_um == pytest.approx(800.0)
    assert core.material_name == "FR4_CORE"

    assert l2.name == "L2_BOT"
    assert l2.type == stackup.LayerType.COPPER
    assert l2.thickness_um == pytest.approx(35.0)
    assert l2.material_name == "COPPER_STD"


def test_parse_layers_missing_name_raises():
    """
    Tests parse_layers missing name. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            # name ommited
            "type": "copper",
            "material": "foo",
            "thickness_um": 35,
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "is missing required field: 'name'" in str(excinfo.value)


def test_parse_layers_missing_type_raises():
    """
    Tests parse_layers missing type. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            # type ommited
            "material": "COPPER_STD",
            "thickness_um": 35,
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "is missing required field: 'type'" in str(excinfo.value)


def test_parse_layers_invalid_type_raises():
    """
    Tests parse_layers invalid type. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "foo",
            "material": "COPPER_STD",
            "thickness_um": 35,
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "has unknown layer type, 'foo' is not a valid LayerType" in str(
        excinfo.value
    )


def test_parse_layers_missing_material_raises():
    """
    Tests parse_layers with missing material. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "copper",
            # material ommited
            "thickness_um": 35,
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "is missing required field: 'material'" in str(excinfo.value)


def test_parse_layers_unknown_material_raises():
    """
    Tests parse_layers with invalid material not present in materials. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "copper",
            "material": "foo",
            "thickness_um": 35,
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "has unknown materials" in str(excinfo.value)


def test_parse_layers_missing_thickness_raises():
    """
    Tests parse_layers with missing thickness_um. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "copper",
            "material": "COPPER_STD",
            # thickness_um ommitted
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "missing required field: 'thickness_um'" in str(excinfo.value)


def test_parse_layers_invalid_thickness_raises():
    """
    Tests parse_layers with invalid thickness_um. Checks if
    the correct InvalidLayers is raised
    """

    materials = _make_materials_for_layers()

    layers_section = [
        {
            "name": "L1_TOP",
            "type": "copper",
            "material": "COPPER_STD",
            "thickness_um": "foo",
        },
    ]

    with pytest.raises(stackup.InvalidLayers) as excinfo:
        stackup.parse_layers(layers_section, materials)

    assert "Input should be a valid num" in str(excinfo.value)


def test_parse_layers_empty_list_ok():
    """
    Tests parse_layers with a empty layer yaml section
    """
    materials = _make_materials_for_layers()
    layers = stackup.parse_layers([], materials)
    assert layers == []
