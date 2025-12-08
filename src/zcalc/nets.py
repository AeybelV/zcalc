"""
Bluh

"""

from enum import Enum
from types import NoneType
from typing import Optional, List

import yaml
from pydantic import BaseModel, ValidationError


# ========== Exceptions ==========


class InvalidNetList(Exception):
    """Raised when the Nets List defintion YAML is invalid."""


# ========== Dataclasses ==========


class Geometry(str, Enum):
    """
    Geometry of the copper for a net

    Attributes:
        AUTO: Automatic
        MICROSTRIP: Microstrip
        STRIPLINE: Stripling
        CPW_GROUND: Coplanar Microstrip with Ground
    """

    AUTO = "auto"
    MICROSTRIP = "microstrip"
    STRIPLINE = "stripline"
    CPW_GROUND = "cpw_ground"


class NetType(str, Enum):
    """
    Signal type for the Net

    Attributes:
        NET_PWR:
        NET_SIG:
        NET_DIFF_SIG:
        NET_RF:
    """

    NET_PWR = "power"
    NET_SIG = "signal"
    NET_DIFF_SIG = "diff_signal"
    NET_RF = "rf"


class NetSpec(BaseModel):
    """
    Specifications/Requirements for a Net

    Attributes:
        name: Net name
        layer: Layer name it resides on
        role: The NetType of the net
        geometry: the Geometry of the net
        z0_target_ohm: Optional Desired single-ended impedance
        zdiff_target_ohm: Optional Desired differential impedance
        i_dc_a: Optional Current Requirements
        temp_rise_c: Optional Thermal Requirements
        length_mm: Optional Trace length
        voltage_v: Optional Voltage the Net resides at
        min_width_mm: Optional  Minimum trace width
        preferred_clearance_mm: Optional Preffered trace dlearance
        ref_plane_above: Optional explicit reference planes above the net (by name).
        These should be copper layers in the stackup
        ref_plane_below: Optional explicit reference planes below the net (by name).
        These should be copper layers in the stackup
        notes: Any notes regarding the net
    """

    name: str
    layer: str
    role: NetType
    geometry: Geometry = Geometry.AUTO

    # Impedance Requirements  (single-ended / differential)
    z0_target_ohm: Optional[float] = None
    zdiff_target_ohm: Optional[float] = None

    # Current / thermal requirements
    i_dc_a: Optional[float] = None
    temp_rise_c: Optional[float] = None

    # Other context
    length_mm: Optional[float] = None
    voltage_v: Optional[float] = None

    # Layout preferences
    min_width_mm: Optional[float] = None
    preferred_clearance_mm: Optional[float] = None

    # Optional explicit reference planes (by name)
    # These should be copper layers in the physical stackup.
    ref_plane_above: Optional[str] = None
    ref_plane_below: Optional[str] = None

    notes: str = ""


# ========== Net Logic ==========


def load_nets(path: str) -> List[NetSpec]:
    """
    Loads and parses a Nets List Defintion File

    Args:
        path: Path to Net List

    Returns:
        Python list of NetSpecs
    """

    # with open()
    nets: List[NetSpec] = []
    yaml_data = None
    try:
        with open(path, "r") as f:
            yaml_data = yaml.safe_load(f)
            if isinstance(yaml_data, NoneType):
                raise InvalidNetList(f"Malformed Net List Defintion {path}")

        nets_data = yaml_data.get("nets", [])

        for nd in nets_data:
            net_name = nd["name"]
            geom_str = nd.get("geometry", "auto")
            geom = Geometry(geom_str)

            try:
                net = NetSpec(
                    name=net_name,
                    layer=nd["layer"],
                    role=nd["role"],
                    geometry=geom,
                    z0_target_ohm=nd.get("z0_target_ohm"),
                    zdiff_target_ohm=nd.get("zdiff_target_ohm"),
                    i_dc_a=nd.get("i_dc_a"),
                    temp_rise_c=nd.get("temp_rise_c"),
                    length_mm=nd.get("length_mm"),
                    voltage_v=nd.get("voltage_v"),
                    min_width_mm=nd.get("min_width_mm"),
                    preferred_clearance_mm=nd.get("preferred_clearance_mm"),
                    ref_plane_above=nd.get("ref_plane_above"),
                    ref_plane_below=nd.get("ref_plane_below"),
                    notes=nd.get("notes", ""),
                )

                nets.append(net)
            except ValidationError as e:
                raise InvalidNetList(
                    f"Netlist validation error for net '{net_name}':\n'{e}'"
                ) from e

        return nets
    except FileNotFoundError as e:
        raise InvalidNetList(f"Net List definition {path}, not found") from e
    except yaml.YAMLError as e:
        print("Invalid Stackup YAML:", e)

    return nets
