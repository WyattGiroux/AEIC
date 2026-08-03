# from typing import Literal

from AEIC.trajectories.segments.segment_base import (
    FlightSegment,
)


class SegmentDefinitions:
    class Max_ROCD_Const_Speed(FlightSegment): ...

    class CFR_ROCD_Const_Speed(FlightSegment): ...

    class Const_ROCD_Const_Speed(FlightSegment): ...

    class Const_Alt_Const_Speed(FlightSegment): ...

    # class CAS_ROCD(FlightSegment):
    #     """Flight segment representing an aircraft flying with a specified calibrated
    #     airspeed and rate of climb/descent"""

    #     SEGMENT_ID = Literal('cas_rocd_segment')

    #     def __init__(self, cas, rocd, interrupts, endpoints):
    #         # cas_rule = FlightRule('cas', cas)
    #         # roc_rule = FlightRule('rocd', rocd)
    #         pass

    #     def _fly_step(traj, perf, is_backwards):
    #         return super()._fly_step(perf, is_backwards)
