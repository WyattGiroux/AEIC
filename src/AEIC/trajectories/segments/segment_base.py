# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import operator as op
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import IntEnum, auto
from typing import Any

from AEIC.performance.models import BasePerformanceModel
from AEIC.trajectories.trajectory import Trajectory


class FlightSegmentBase(ABC):
    """Defines a segment of an aircraft's vertical trajectory given starting from a
    known point and traversing until one (or more) conditions are met as defined by the
    relevant `SegmentInterrupt` objects.

    Aircraft performance is determined by passing altitude, aircraft mass, and *up to* 2
    "flight rules" to a performance model. The segments runnable by a given performance
    model are defined in `AEIC.performance.allowed_segments`.

    Attributes:
        rules (list[FlightRule]): list of flight rules to be used
        exceptions(list[SegmentInterrupt]): list of interrupt conditions
    """

    def __init__(
        self,
        rules: list[FlightRule],
        exceptions: list[SegmentInterruptBase] = None,
    ) -> None:
        self.rules = rules
        self.exceptions = exceptions
        self.run_backwards = False

        # Check to make sure at least one NEXT code is present in any given segment.
        # Without one, it may be possible for the trajectory to throw an error due to
        # exceeding step limits.
        no_next_code = True
        for excep in self.exceptions:
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
        for excep in self.exceptions:
            if excep.check_condition(traj):
                return True, (excep.code, excep.interrupt_return_data)
        return False, None

    @abstractmethod
    def _fly_step(
        traj: Trajectory,
        perf: BasePerformanceModel,
        is_backwards: bool,
    ):
        """Function to fly an individual step of a mission; to be defined by individual
        FlightSegment children.
        """
        ...


# TODO: Should these be check for validity against the performance model or should the
# segments (or both)?
class FlightRule:
    """Simple representation of a key value pair which can be evaluated against a
    performance model. Standalone class for readability and to allow for validation
    methods in the future.
    """

    def __init__(self, var: str, val: float):
        self.var = var
        self.val = val


class SegmentInterruptBase:
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

    # Could replace with passing in op.xx directly; provide examples
    _ops = {
        '==': op.eq,
        '!=': op.ne,
        '<': op.lt,
        '<=': op.le,
        '>': op.gt,
        '>=': op.ge,
    }

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

    def __init__(
        self,
        var: str,
        value: float,
        oper: str,
        code: InterruptCode = InterruptCode.NEXT,
        insert_segments: list[FlightSegmentBase] | None = None,
        user_method: Callable[..., Trajectory] | None = None,
    ):
        self.var = var
        self.val = value
        if oper not in self._ops:
            raise KeyError(f'Invalid Operator: {oper}')
        self.oper = self._ops[oper]
        self.code = code

        # These should only be defined (not None) if using INSERT, INSERT_NEXT, or
        # USER_DEFINED codes
        self.insert_segments = insert_segments
        self.user_method = user_method

        if self.insert_segments is not None and (
            code is not self.InterruptCode.INSERT
            or code is not self.InterruptCode.INSERT_NEXT
        ):
            raise ValueError(
                'Interrupt code must be INSERT or INSERT_NEXT when passing in'
                ' `insert_segments`.'
            )
        if self.user_method is not None and code is not self.InterruptCode.USER_DEFINED:
            raise ValueError(
                'Interrupt code must be USER_METHOD when passing in `user_method`.'
            )

        # Set when the interrupt is triggered depending on the selected code
        self.interrupt_return_data = None

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
                self.interrupt_return_data = self.insert_segments
            case self.InterruptCode.USER_DEFINED:
                self.interrupt_return_data = self.user_method
            case _:
                pass
        return True


class SegmentEnd(SegmentInterruptBase):
    """Interrupt trigger primarily wrapping the default NEXT behavior in the
    SegmentInterrupt. Provides a dedicated object for creating end conditions
    for segments.
    """

    def __init__(self, var: str, val: float, oper: str):
        super().__init__(var, val, oper)
