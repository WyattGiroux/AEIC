from typing import Literal

from AEIC.trajectories.segments.segment_base import (
    FlightSegmentBase,
    SegmentInterruptBase,
)

# import AEIC.trajectories.segments as sd
#
# seg1 = sd.Max_ROCD_Const_Speed


class CFR_ROCD_Const_CAS(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_cas']
    """Segment type identifier for TOML input files."""

    cas: float
    """Calibrated airspeed of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    interrupts: list[SegmentInterruptBase]
    """Dictionary of ``SegementInterrupts"""


class CFR_ROCD_Const_Mach(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_mach']
    """Segment type identifier for TOML input files"""

    mach: float
    """Mach number of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    interrupts: list[SegmentInterruptBase]
    """Dictionary of ``SegementInterrupts"""


class Const_Alt_Const_Mach(FlightSegmentBase):
    segment_type: Literal['const_alt_const_mach']
    """Segment type identifier for TOML input files"""
