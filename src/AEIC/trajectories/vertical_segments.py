from dataclasses import dataclass


class FlightSegment:
    def __init__(self, rules, end_conditions):
        self.rules = rules
        self.end_conds = end_conditions


@dataclass
class FlightRule:
    var: str
    val: float | str


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
