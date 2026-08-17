from pathlib import Path

# from AEIC.performance.allowed_segments import ALLOWED_SEGMENTS
from AEIC.performance.models import BasePerformanceModel


class TrajectorySchedule:
    def __init__(self, path: str | Path):
        self.climb = []
        self.cruise = []
        self.descent = []

    def validate(self, perf: BasePerformanceModel) -> bool:
        """Check for compatability of all TrajectorySegments with the selected
        performance model
        """
        pass
