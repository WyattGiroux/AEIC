# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import tomllib
from pathlib import Path

from AEIC.config import config
from AEIC.performance.models import BasePerformanceModel

# from AEIC.performance.allowed_segments import ALLOWED_SEGMENTS
from AEIC.trajectories.segments import FlightSegment


class TrajectorySchedule:
    """Container and validator for a given vertical trajectory specification. Stores
    climb, cruise, and descent lists of ``FlightSegmentBase`` objects.

    Attributes:
        climb (list[FlightSegmentBase]): Ordered list of climb segments.
        cruise (list[FlightSegmentBase]): Ordered list of cruise segments.
        descent (list[FlightSegmentBase]): Reverse-chronological list of descent
            segments.
    """

    def __init__(self, path: str | Path):
        with open(config.file_location(path), 'rb') as fp:
            data = tomllib.load(fp)

            # Normalize climb, cruise, descent casing
            data = {k.lower(): v for k, v in data.items()}

        if 'climb' not in data:
            raise KeyError("``climb`` must appear as a key in the root trajectory")
        self.climb = self.load_phase_from_dict(data, 'climb')

        if 'cruise' not in data:
            raise KeyError("``cruise`` must appear as a key in the root trajectory")
        self.cruise = self.load_phase_from_dict(data, 'cruise')

        if 'descent' not in data:
            raise KeyError("``descent`` must appear as a key in the root trajectory")
        self.descent = self.load_phase_from_dict(data, 'descent')

    def load_phase_from_dict(self, data: dict, phase: str):
        return [FlightSegment.load_from_dict(seg) for _, seg in data[phase].items()]

    def validate(self, perf: BasePerformanceModel):
        """Check for compatability of all TrajectorySegments with the selected
        performance model
        """
        # TODO: potentially replace with Enum?
        for phase in ['climb', 'cruise', 'descent']:
            if not self._validate_phase(perf, phase):
                raise ValueError(f'{phase.upper()} segments failed to validate.')

    def _validate_phase(self, perf: BasePerformanceModel, phase: str) -> bool:
        """Call validation on a specific phase. Return false if any segments fail."""
        return not any([seg.validate(perf) for seg in getattr(self, phase)])
