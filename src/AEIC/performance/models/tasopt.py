from typing import Literal

from AEIC.performance.types import SimpleFlightRules

from .base import BasePerformanceModel


class TASOPTPerformanceModel(BasePerformanceModel[SimpleFlightRules]):
    model_type: Literal['TASOPT']

    max_range_km: float

    cruise_mach: float

    @property
    def empty_mass(self):
        pass

    @property
    def maximum_mass(self):
        pass

    def evaluate_impl(self):
        pass
