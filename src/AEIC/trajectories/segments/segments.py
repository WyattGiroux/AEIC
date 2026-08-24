# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import operator as op
from typing import Literal

from pydantic import model_validator

from AEIC.trajectories.segments.segment_base import (
    FlightSegmentBase,
    SegmentEnd,
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

    @model_validator(mode='after')
    def set_next(self):
        self.interrupts.append(
            SegmentEnd(var='altitude', value=self.end_alt, oper=op.gt)
        )
        self.validate_next_exists()

    def _fly_step(self, traj, perf, is_backwards):
        pass


class CFR_ROCD_Const_Mach(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_mach']
    """Segment type identifier for TOML input files"""

    mach: float | str
    """Mach number of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    @model_validator(mode='after')
    def set_next(self):
        self.interrupts.append(
            SegmentEnd(var='altitude', value=self.end_alt, oper=op.gt)
        )
        self.validate_next_exists()

    def _fly_step(self, traj, perf, is_backwards):
        pass


class Const_Alt_Const_Mach(FlightSegmentBase):
    segment_type: Literal['const_alt_const_mach']
    """Segment type identifier for TOML input files"""

    def _fly_step(self, traj, perf, is_backwards):
        pass

    @model_validator(mode='after')
    def set_next(self):
        # TODO this is a temporary "toy" interrupt for testing
        self.interrupts.append(SegmentEnd(var='altitude', value=1, oper=op.gt))
        self.validate_next_exists()
