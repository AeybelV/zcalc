"""
ZCalc Stackup Logic
"""

from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Any, Dict, List, Mapping, Optional, Literal

import yaml
from pydantic import BaseModel, ValidationError

# ========== Exceptions ==========


class InvalidStackup(Exception):
    """Raised when the Stackup defintion YAML is invalid."""


class InvalidMaterials(Exception):
    """Raised when the materials section in YAML is invalid."""


class InvalidLayers(Exception):
    """Raised when the layers section in YAML is invalid."""


# ========== Dataclasses and Enums ==========


class LayerType(str, Enum):
    """
    Enum describing the layer type

    Attributes:
        COPPER: Copper layer. Such as copper foil and plating, wires, signals, planes, etc
        DIELECTRIC: Dielectric Layer, Such as FR4-core, prepeg, solder mask, etc
    """

    COPPER = "copper"
    DIELECTRIC = "dielectric"


class Material(BaseModel):
    """
    Physical Material used in the stackup

    Attributes:
        name: Name of the material
        kind: Material Type (Dielectric or copper)
        er: Dielectric Constant
        conductivity: Conductivity of a material S per M
    """

    name: str
    kind: Literal["dielectric", "copper"]
    er: Optional[float] = None
    conductivity: Optional[float] = None


class StackLayer(BaseModel):
    """
    Represents a single physical layer in the PCB stack

    Attributes:
        name: Name of the layer
        type: LayerType enum
        index: Layer number
        thickness_um: Layer thickness
        material_name: Material reference name from materials section in a stackup definition
    """

    name: str
    type: LayerType
    index: int
    thickness_um: float
    # Material Reference (refers to stackup.materials section in a stackup definition)
    material_name: str


@dataclass
class Stackup:
    """
    Full physical stackup description, including materials

    Attributes:
        name: Stackup name
        layers: A List of StackLayers
        layers_by_name: A mapping of layer names to StackLayers
        materials: Materials section in a stackup definition. Contains Material Characteristics
        fab_min_trace_mm: Mininimum trace width
        fab_min_clearance_mm: Minimum clearance
        fab_max_copper_oz: Maximum copper weight
    """

    name: str
    layers: List[StackLayer]
    layers_by_name: Dict[str, StackLayer]
    materials: Dict[str, Material]
    fab_min_trace_mm: float
    fab_min_clearance_mm: float
    fab_max_copper_oz: float


# =========== Utilities ==========


def parse_materials(materials_data: Any) -> Dict[str, Material]:
    """
    Constructs a mapping of a material name to a Material Data Class

    Args:
        materials_data: YAML data corresponding to materials sections

    Returns:
        Mapping of material name to the Material and its material properties

    Raises:
        InvalidMaterials: Materials Section is Malformed
    """
    if not isinstance(materials_data, Mapping):
        raise InvalidMaterials("`materials` must be a mapping (dict) in YAML.")

    materials: Dict[str, Material] = {}

    for name, md in materials_data.items():
        if not isinstance(md, Mapping) or isinstance(md, NoneType):
            raise InvalidMaterials(f"Material '{name}' must be a mapping")

        if "kind" not in md:
            raise InvalidMaterials(
                f"Material '{name}' is missing required field: 'kind'."
            )

        kind = md["kind"]

        try:
            mat = Material(
                name=name,
                kind=kind,
                er=md.get("er"),
                conductivity=md.get("conductivity"),
            )
        except ValidationError as e:
            raise InvalidMaterials(f"Material '{name}' validation error:\n'{e}'") from e

        materials[name] = mat

    return materials


def parse_layers(
    layers_data: Any, materials: Optional[Dict[str, Material]]
) -> List[StackLayer]:
    """
    Constructs a list containing StackLayers representing layer properties

    Args:
        layers_data: YAML data corresponding to a layers section

    Returns:
        List of StackLayer representations of layer properties


    Raises:
        InvalidLayers: Layers Section is Malformed
    """

    if not isinstance(layers_data, List):
        raise InvalidLayers("`layers` must be a mapping (dict) in YAML.")

    layers: List[StackLayer] = []

    for idx, ld in enumerate(layers_data):
        # Property sanity checks
        if not isinstance(ld, Mapping) or isinstance(ld, NoneType):
            raise InvalidLayers(f"Layer at index '{idx}' must be a mapping")

        if "name" not in ld:
            raise InvalidLayers(
                f"Layer at index '{idx}' is missing required field: 'name'."
            )

        if "type" not in ld:
            raise InvalidLayers(
                f"Layer at index '{idx}' is missing required field: 'type'."
            )

        if "material" not in ld:
            raise InvalidLayers(
                f"Layer at index '{idx}' is missing required field: 'material'."
            )

        if "thickness_um" not in ld:
            raise InvalidLayers(
                f"Layer at index '{idx}' is missing required field: 'thickness_um'."
            )

        # Makes sure the layer type is a valid enuum
        try:
            layer_type = LayerType(ld["type"])
        except ValueError as e:
            raise InvalidLayers(
                f"""Layer at index '{idx}' has unknown layer type, {e}"""
            ) from e

        # If a materials mapping is given, make sure the material listed
        # in the layer is in the mapping
        mat_name = ld["material"]
        if materials is not None and mat_name not in materials:
            raise InvalidLayers(
                f"Layer at index '{idx}' is has unknown materials '{mat_name}'"
            )

        # Construct layer class. Model class will throw error if type mismatches or missing fields
        try:
            layer = StackLayer(
                name=ld["name"],
                type=layer_type,
                index=idx,
                thickness_um=ld["thickness_um"],
                material_name=mat_name,
            )
        except ValidationError as e:
            raise InvalidLayers(
                f"Layer at index '{idx}' validation error:\n'{e}'"
            ) from e

        layers.append(layer)

    return layers


# =========== Stackup Manipulation ==========


def load_stackup(path: str) -> Stackup:
    """
    Loads a stackup defintion file, parses it, and returns a Stackup dataclass
    Args:
        path: Path to stackup defintion

    Returns:
       Stackup representing the parsed stackup defintion
    """

    yaml_data = None

    try:
        with open(path, "r") as f:
            yaml_data = yaml.safe_load(f)

        materials = parse_materials(yaml_data.get("materials", {}))
        parse_layers(yaml_data.get("layers", {}), materials)

    except InvalidMaterials as e:
        raise InvalidStackup(f"Error in Stackup Definition: {e}") from e
    except InvalidLayers as e:
        raise InvalidStackup(f"Error in Stackup Definition: {e}") from e
    except yaml.YAMLError as e:
        print("Invalid Stackup YAML:", e)

    # Materials
