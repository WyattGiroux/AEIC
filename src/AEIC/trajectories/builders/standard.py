from dataclasses import dataclass

from AEIC.missions import Mission
from AEIC.performance.models import PerformanceModel

from .. import Trajectory
from .base import Builder, Context, Options


@dataclass
class StandardOptions: ...


class StandardContext(Context):
    def __init__(
        self,
        builder: 'StandardBuilder',
        ac_performance: PerformanceModel,
        mission: Mission,
        starting_mass: float | None,
    ):
        raise NotImplementedError('StandardContext is not yet implemented.')


class StandardBuilder(Builder):
    """."""

    CONTEXT_CLASS = StandardContext

    def __init__(
        self,
        options: Options = Options(),
        standard_options: StandardOptions = StandardOptions(),
    ):
        raise NotImplementedError('StandardBuilder is not yet implemented.')
        super().__init__(options)

    def calc_starting_mass(self) -> float: ...

    def climb(self, traj: Trajectory) -> None: ...

    def cruise(self, traj: Trajectory) -> None: ...

    def descent(self, traj: Trajectory) -> None: ...
