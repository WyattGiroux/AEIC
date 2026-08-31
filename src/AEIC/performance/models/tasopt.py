from typing import Literal

from AEIC.performance.types import SimpleFlightRules

from .base import BasePerformanceModel


class TASOPTPerformanceModel(BasePerformanceModel[SimpleFlightRules]):
    model_type: Literal['TASOPT']
    ...

    @property
    def empty_mass(self):
        pass

    @property
    def maximum_mass(self):
        pass

    def evaluate_impl(self):
        pass
