"""
Bluh

"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Literal, List

from pydantic import BaseModel


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
