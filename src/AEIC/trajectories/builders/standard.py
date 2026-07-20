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
        raise NotImplementedError('DymosContext is not yet implemented.')


class StandardBuilder(Builder):
    """Model for determining flight trajectories using ADS-B flight data. Can
    be optimized using methods defined by Marek Travnik."""

    CONTEXT_CLASS = StandardContext

    def __init__(
        self,
        options: Options = Options(),
        tasopt_options: StandardOptions = StandardOptions(),
    ):
        raise NotImplementedError('StandardBuilder is not yet implemented.')
        super().__init__(options)

    def calc_starting_mass(self) -> float: ...

    def climb(self, traj: Trajectory) -> None: ...

    def cruise(self, traj: Trajectory) -> None: ...

    def descent(self, traj: Trajectory) -> None: ...
