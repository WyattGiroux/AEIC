import tomllib
from pathlib import Path

from AEIC.config import config

# from AEIC.performance.allowed_segments import ALLOWED_SEGMENTS
from AEIC.performance.models import BasePerformanceModel


class TrajectorySchedule:
    def __init__(self, path: str | Path):

        with open(config.file_location(path), 'rb') as fp:
            _ = tomllib.load(fp)

        self.climb = []
        self.cruise = []
        self.descent = []

    def validate(self, perf: BasePerformanceModel) -> bool:
        """Check for compatability of all TrajectorySegments with the selected
        performance model
        """
        pass
