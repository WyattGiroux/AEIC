from enum import IntEnum, auto


class FlightSegment:
    def __init__(
        self, rules: dict[str, str | float], end_conditions, exceptions=None
    ) -> None:
        self.rules = rules
        self.end_conds = end_conditions
        self.exceptions = exceptions


class SegmentInterrupt:
    """Object for representing dynamic conditions on a segment of a flight which may
    modify or end the segment early. An example use case would be integrating dynamic
    step climbs in cruise:

        - If below a minimum CL, trigger the interrupt and insert a climb with end
          condition of being above a maximum CL, then resume cruise.
    """

    def __init__(self):
        pass

    class InterruptCode(IntEnum):
        """Prescribed interrupt actions.

        Options:
            - NEXT: End current segment and move to next in list.
            - INSERT: Pause current segment and insert segments before continuing.
            - USER_DEFINED: Execute a user-defined method.
        """

        NEXT = auto()
        INSERT = auto()
        USER_DEFINED = auto()

    class Exception(Exception):
        """Exception raised when interrupting a trajectory segment."""

        ...


class SegmentEnd(SegmentInterrupt):
    """Interrupt trigger primarily wrapping the NEXT behavior in the SegmentInterrupt.
    Provides a simplified framework for creating end conditions for segments.
    """

    def __init__(self):
        super().__init__()
