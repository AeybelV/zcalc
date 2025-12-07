"""
ZCalc Stackup Logic
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Literal

import yaml

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


@dataclass
class Material:
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


@dataclass
class StackLayer:
    """
    Represents a single physical layer in the PCB stack

    Attributes:
        name: Name of the layer
        type: LayerType enum
        index: Layer number
        copper_thickness_um: Copper layer thickness
        thickness_um: Dielectric Layer thickness
        material_name: Material reference name from materials section in a stackup definition
    """

    name: str
    type: LayerType
    index: int

    # For Copper Layers
    copper_thickness_um: Optional[float] = None

    # For Dielectric Layers
    thickness_um: Optional[float] = None

    # MAterial Reference (refers to stackup.materials section in a stackup definition)
    material_name: Optional[str] = None


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


def parse_materials(yaml_data: Any) -> Dict[str, Material]:
    """
    Constructs a mapping of a material name to a Material Data Class

    Args:
        yaml_data: YAML data corresponding to materials sections

    Returns:
        Mapping of material name to the Material and its material properties

    """
    materials_data = yaml_data.get("materials", {})
    materials: Dict[str, Material] = {}

    for name, md in materials_data.items():
        kind = md["kind"]
        mat = Material(
            name=name, kind=kind, er=md.get("er"), conductivity=md.get("conductivity")
        )

        materials[name] = mat

    return materials


# =========== Stackup Manipulation ==========


def load_stackup(path: str) -> Stackup:
    """
    Loads a stackup defintion file, parses it, and returns a Stackup dataclass
    Args:
        path: Path to stackup defintion

    Returns:
       Stackup representing the parsed stackup defintion
    """

    with open(path, "r") as f:
        yaml_data = yaml.safe_load(f)

    # Materials
    matterials = parse_materials(yaml_data.get("materials", {}))
