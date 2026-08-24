# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

# import operator as op
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import IntEnum, auto
from typing import Any

from pydantic import PrivateAttr, model_validator

from AEIC.performance.models import BasePerformanceModel
from AEIC.trajectories.trajectory import Trajectory
from AEIC.utils.models import CIBaseModel, CIStrEnum


class FlightSegmentBase(CIBaseModel, ABC):
    """Defines a segment of an aircraft's vertical trajectory given starting from a
    known point and traversing until one (or more) conditions are met as defined by the
    relevant `SegmentInterrupt` objects.

    Aircraft performance is determined by passing altitude, aircraft mass, and *up to* 2
    "flight rules" to a performance model. The segments runnable by a given performance
    model are defined in `AEIC.performance.allowed_segments`.

    Attributes:
        rules (list[FlightRule]): list of flight rules to be used
        interrupts(list[SegmentInterrupt]): list of interrupt conditions
    """

    interrupts: list[SegmentInterruptBase] = []

    def validate_next_exists(self):
        # Check to make sure at least one NEXT code is present in any given segment.
        # Without one, it may be possible for the trajectory to throw an error due to
        # exceeding step limits.
        no_next_code = True
        for excep in self.interrupts:
            if excep.code is SegmentInterruptBase.InterruptCode.NEXT:
                no_next_code = False

        if no_next_code:
            raise ValueError('Each segment must have a NEXT interrupt.')

    def __call__(
        self,
        traj: Trajectory,
        perf: BasePerformanceModel,
        is_backwards: bool,
        step_lim: int = 1000,
    ) -> tuple[Trajectory, SegmentInterruptBase.InterruptCode, Any]:
        """Runs the flight segment starting from idx -1 in the `traj` object. Runs until
        an interrupt is reached or a number of steps set by `step_lim` are taken. If the
        step limit is exceeded, the flight raises an error.

        Arguments:
            traj (Trajectory): The trajectory container.
            perf (BasePerformanceModel): The performance model being used.
            is_backwards (bool): Controls whether the segment is forward/backwards
                marching with respect to time.
            step_lim (int): Maximum number of steps allowable before error is raised.

        Returns:
            traj (Trajectory): Trajectory with the segment data appended.
            code (SegmentInterrupt.InterruptCode): Code with which the segment was ended
            return_data: Either list of segments to be inserted or a callable method.
        """
        for _ in range(step_lim):
            trigger, interrupt = self._check_interrupts(traj)

            if trigger:
                # we can remove traj; its the same object being mutated
                return traj, *interrupt

            # traj.append(self._fly_step())
            traj = self._fly_step(traj, perf, is_backwards)

        raise RuntimeError(
            f'Segment failed to run in {step_lim} steps; aborting flight.'
        )

    def _check_interrupts(self, traj: Trajectory):
        """Check to see whether any interrupts have triggered."""
        for itp in self.interrupts:
            if itp.check_condition(traj):
                return True, (itp.code, itp.interrupt_return_data)
        return False, None

    @abstractmethod
    def _fly_step(
        self,
        traj: Trajectory,
        perf: BasePerformanceModel,
        is_backwards: bool,
    ):
        """Function to fly an individual step of a mission; to be defined by individual
        FlightSegment children.
        """
        ...

    def validate(self, perf: BasePerformanceModel):
        """Checks that the segment and all interrupts are compatible with the selected
        performance model.

        Note: import of ALLOWED_SEGMENTS / ALLOWED_INTERRUPTS is done locally here to
        avoid a circular import at module import time between
        AEIC.performance.allowed_segments and AEIC.trajectories.segments.
        """
        # Local import to avoid circular import during module initialization
        from AEIC.performance.allowed_segments import (
            ALLOWED_INTERRUPTS,
            ALLOWED_SEGMENTS,
        )

        if type(self) not in ALLOWED_SEGMENTS[type(perf)]:
            raise ValueError(f'Segment {type(self)} is not useable with {type(perf)}.')

        for interrupt in self.interrupts:
            if type(interrupt) not in ALLOWED_INTERRUPTS[type(perf)]:
                raise ValueError(
                    f'Interrupt {type(interrupt)} not useable with {type(perf)}.'
                )


class SegmentInterruptBase(CIBaseModel):
    """Object for representing dynamic conditions on a segment of a flight which may
    modify or end the segment early. An example use case would be integrating dynamic
    step climbs in cruise:

        - If below a minimum CL, trigger the interrupt and insert a climb with end
          condition of being above a maximum CL, then resume cruise.

    Attributes:
        var (str): name of the variable which triggers the interrupt (must be part of
            the trajectory fields)
        value (float): value at which the interrupt is triggered
        oper (str): string of the binary operator used in the comparison oper(var,value)
    """

    # TODO: Can get rid of INSERT_NEXT; collapse to single INSERT
    class InterruptCode(IntEnum):
        """Prescribed interrupt actions.

        Options:
            - NEXT: End current segment and move to next in list.
            - INSERT_NEXT: End current segment and insert segments before the running
                the next segment.
            - INSERT: Pause current segment and insert segments before returning to
                paused segment
            - USER_DEFINED: Execute a user-defined method.
        """

        NEXT = auto()
        INSERT_NEXT = auto()
        INSERT = auto()
        USER_DEFINED = auto()

    var: str
    """Name of the tracked variable in the trajectory store."""

    value: float | str
    """Value of the value on which to trigger events."""

    oper: Callable[[float, float], bool]
    """Comparison operator between var and value, in that order."""

    code: InterruptCode
    """Interrupt code determining action to take on trigger."""

    insert_segments: list[FlightSegmentBase] | None = None
    """Segments to insert on a INSERT trigger."""

    user_method: Callable[..., Trajectory] | None = None
    """User-defined function to call on a USER_DEFINED trigger."""

    _interrupt_return_data: Any | None = PrivateAttr()
    """Private variable used to return information to a Segment when triggered."""

    @model_validator(mode='after')
    def setup(self):
        if self.insert_segments is not None and (
            self.code is not self.InterruptCode.INSERT
            or self.code is not self.InterruptCode.INSERT_NEXT
        ):
            raise ValueError(
                'Interrupt code must be INSERT or INSERT_NEXT when passing in'
                ' `insert_segments`.'
            )
        if (
            self.user_method is not None
            and self.code is not self.InterruptCode.USER_DEFINED
        ):
            raise ValueError(
                'Interrupt code must be USER_METHOD when passing in `user_method`.'
            )

        # Set when the interrupt is triggered depending on the selected code
        self._interrupt_return_data = None

    def validate(self, traj: Trajectory):
        """Validate that a trajectory store is tracking the trigger variable."""
        assert hasattr(traj, self.var)

    def check_condition(self, traj: Trajectory):
        """Checks to see if the most recent trajectory point should trigger the
        interrupt
        """
        newest_value = getattr(traj, self.var)[-1]
        if self.oper(newest_value, self.val):
            self._trigger()
        return False

    def _trigger(self):
        """Raises SegmentInterrupt.Exception with the interrupt code and relevant data
        for the FlightSegment to perform final checks and return
        """
        match self.code:
            case self.InterruptCode.INSERT:
                self._interrupt_return_data = self.insert_segments
            case self.InterruptCode.USER_DEFINED:
                self._interrupt_return_data = self.user_method
            case _:
                pass
        return True


class SegmentEnd(SegmentInterruptBase):
    """Interrupt trigger primarily wrapping the default NEXT behavior in the
    SegmentInterrupt. Provides a dedicated object for creating end conditions
    for segments.
    """

    var: str
    """Name of the tracked variable in the trajectory store."""

    value: float | str
    """Value of the value on which to trigger events."""

    oper: Callable[[float, float], bool]
    """Comparison operator between var and value, in that order."""

    code: SegmentInterruptBase.InterruptCode = SegmentInterruptBase.InterruptCode.NEXT
    """Interrupt code determining action to take on trigger."""

    insert_segments: list[FlightSegmentBase] | None = None
    """Segments to insert on a INSERT trigger."""

    user_method: Callable[..., Trajectory] | None = None
    """User-defined function to call on a USER_DEFINED trigger."""


class ACOperationState(CIBaseModel):
    altitude: float
    """Altitude [m]."""

    aircraft_mass: float
    """Aircraft total mass [kg]."""

    rules: list[FlightRule]
    """Operating state control variables to be applied to a performance model. Can be
    empty, length 1, or length 2, depending on what a performance model requires."""

    @model_validator(mode='after')
    def prevent_overdefined(self):
        if len(self.rules) > 2:
            raise ValueError('At most two ``rules`` can be specified.')


class FlightRule:
    """Standardized container format for passing aircraft operating rules to a
    performance model.
    """

    control_var: ControlVar
    """Control variable of interest"""

    value: float
    """Value of the control variable"""


class ControlVar(CIStrEnum):
    """Valid control variables to be passed as part of a FlightRule to a performance
    model. All dimensions are assumed to be SI.

    Attributes:
        THROTTLE_PCT: Percent maximum throttle setting (%)
        THROTTLE_FRAC: Fraction of maximum throttle
        CAS: Calibrated airspeed (m/s)
        TAS: True airspeed (m/s)
        IAS: Indicated airspeed (m/s)
        EAS: Effective airspeed (m/s)
        ROCD: Rate of climb/descent (m/s)
        GRADIENT: Climb/descent gradient (ROCD / Horizontal Speed)
        FLIGHT_ANGLE: Angle of forward motion relative to the horizontal (degree)
    """

    # Engine controls
    THROTTLE_PCT = 'throttle_pct'

    # Airspeeds
    CAS = 'cas'
    TAS = 'tas'
    IAS = 'ias'
    EAS = 'eas'

    # Yoke inputs
    ROCD = 'rocd'
    GRADIENT = 'gradient'
    FLIGHT_ANGLE = 'flight_angle'
