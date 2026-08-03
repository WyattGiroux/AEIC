from AEIC.performance.models import BasePerformanceModel
from AEIC.trajectories import Trajectory
from AEIC.trajectories.segments.flight_segment import FlightSegment


class CAS_ROCD(FlightSegment):
    """Flight segment representing an aircraft flying with a specified calibrated
    airspeed and rate of climb/descent"""

    # Replace entries with enumerator representation or names directly from
    # perf/__init__.py?
    #
    # Checking to make sure the selected perf model is valid would occur one level up in
    # the TrajectorySchedule
    VALID_PERF_MODELS = [
        'TASOPT',
        'BADA-4-OPF',
    ]

    def __init__(self, cas, rocd, interrupts, endpoints):
        self.cas = cas
        self.rocd = rocd
        self.interrupts = interrupts
        self.endpoints = endpoints

    def __call__(self, traj: Trajectory, perf: BasePerformanceModel):
        # This function would take the trajectory object and performance model
        # and run until interrupt/endpoint conditions are met
        pass


# TrajSchedule:
#     CLIMB = [CAS_ROC_Climb, Mach_ROC_Climb]
#     CRUISE = [Const_alt_CRZ, CA]
