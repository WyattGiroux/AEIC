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
        self.climb = [FlightSegment(seg) for seg in data['climb']]

        if 'cruise' not in data:
            raise KeyError("``cruise`` must appear as a key in the root trajectory")
        self.cruise = [FlightSegment(seg) for seg in data['cruise']]

        if 'descent' not in data:
            raise KeyError("``descent`` must appear as a key in the root trajectory")
        self.descent = [FlightSegment(seg) for seg in data['descent']]

    def validate(self, perf: BasePerformanceModel) -> bool:
        """Check for compatability of all TrajectorySegments with the selected
        performance model
        """
        # TODO: potentially replace with Enum?
        for phase in ['climb', 'cruise', 'descent']:
            if not self._validate_phase(perf, phase):
                raise ValueError(f'{phase.upper()} segments failed to validate.')
        return True

    def _validate_phase(self, perf: BasePerformanceModel, phase: str) -> bool:
        """Call validation on a specific phase. Return false if any segments fail."""
        return not any([seg.validate(perf) for seg in getattr(self, phase)])
