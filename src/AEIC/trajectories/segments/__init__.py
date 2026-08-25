# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field, RootModel, model_validator

from .segment_base import FlightSegmentBase, SegmentEnd, SegmentInterruptBase
from .segments import (
    CFR_ROCD_Const_CAS,
    CFR_ROCD_Const_Mach,
    Const_Alt_Const_Mach,
)

SegmentUnion = Annotated[
    (Const_Alt_Const_Mach | CFR_ROCD_Const_Mach | CFR_ROCD_Const_CAS),
    Field(discriminator='segment_type'),
]
"""Union type representing all supported flight segment types. This is a Pydantic
discriminated union, using ``segment_type`` field to guide the actual type of flight
segment instantiated when parsing trajectories from TOML files."""


class FlightSegment(RootModel[SegmentUnion]):
    """Flight segment loader.

    This is a wrapper class to implement loading of flight segments from TOML data.
    """

    @model_validator(mode='before')
    @classmethod
    def normalize_segment_type(cls, data: Any) -> Any:
        """Ensure FlightSegementBase names passed are case-insensitive."""
        if isinstance(data, dict) and 'segment_type' in data:
            data = {**data, 'segment_type': data['segment_type'].lower()}
        return data

    @classmethod
    def load_from_dict(cls, seg_data: dict) -> SegmentUnion:
        """Load a FlightSegmentBase object from a trajectory sub-dictionary.

        The specific segment used is determiend by the ``segment_type`` field
        in the TOML data."""
        return cls.model_validate(seg_data).root


# Rebuild the FlightSegment RootModel to resolve forward references
# caused by circular imports. SegmentInterruptBase and other related model
# classes may be defined after FlightSegment is created, so Pydantic needs a
# second pass to link them together.
FlightSegment.model_rebuild()

__all__ = [
    'FlightSegment',
    'FlightSegmentBase',
    'SegmentInterruptBase',
    'SegmentEnd',
    'SegmentDefinitions',
    'InterruptDefinitions',
]
