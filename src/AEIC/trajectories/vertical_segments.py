class FlightSegment:
    def __init__(self, rules, end_conditions, exceptions=None):
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

    class Exception(Exception):
        """Exception raised when interrupting a trajectory segment."""

        ...

    # trigger = gd_specified
    # todo = deviation (climb, crusie, descent)

    # raise SegmentInterrupt.Exception

    # ... run the deviation ...

    # return to main cruise


def parse_trajectory_segments(raw_traj):
    """Parser to take the toml version of a trajectory definition and convert it to
    ordered lists representing climb, cruise, and desccent.

    Attributes:
        raw_traj (dict): Dictionary representation of the trajectory read in from the
            specified trajectory toml file.

    Returns:
        climb_segments (list[FlightSegment]): Ordered list of flight rules for climb
        cruise_segments (list[FlightSegment]): Ordered list of flight rules for cruise
        descent_segments (list[FlightSegment]): Ordered list of flight rules for descent
    """
