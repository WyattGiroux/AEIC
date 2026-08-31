# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

from AEIC.trajectories import TrajectorySchedule
from AEIC.trajectories.segments import (
    CFR_ROCD_Const_CAS,
    CFR_ROCD_Const_Mach,
    Const_Alt_Const_Mach,
    SegmentEnd,
)

from .models import (
    LegacyPerformanceModel,
    TASOPTPerformanceModel,
)

ALLOWED_SEGMENTS = {
    LegacyPerformanceModel: [],  # StandardBuilder cannot use Legacy models
    TASOPTPerformanceModel: [
        CFR_ROCD_Const_Mach,
        CFR_ROCD_Const_CAS,
        Const_Alt_Const_Mach,
    ],
}

ALLOWED_INTERRUPTS = {
    LegacyPerformanceModel: [],  # StandardBuilder cannot use Legacy models
    TASOPTPerformanceModel: [
        SegmentEnd,
    ],
}


# ALLOWED_INTERRUPTS will need to be added to ensure trajectory schedules are valid
# before simulation begins.


def validate_trajectory_schedule(schedule: TrajectorySchedule, perf_type):
    """Validate whether all segments specified in a ``TrajectorySchedule`` are useable
    with a given performance model.
    """
    seg_allowed = ALLOWED_SEGMENTS[perf_type]
    inter_allowed = ALLOWED_INTERRUPTS[perf_type]

    # Validate climb segments
    climb = schedule.climb
    _validate_phase(climb, seg_allowed, inter_allowed, perf_type)

    # Validate cruise segments
    cruise = schedule.cruise
    _validate_phase(cruise, seg_allowed, inter_allowed, perf_type)

    # Validate descent segments
    descent = schedule.descent
    _validate_phase(descent, seg_allowed, inter_allowed, perf_type)


def _validate_phase(
    phase,
    seg_allowed,
    inter_allowed,
    perf_type,
):
    """Run segment/performance model validation for a single phase."""
    for seg in phase:
        # Check that the overall segment is allowed.
        if type(seg) not in seg_allowed:
            raise ValueError(
                f'Segment of type {type(seg)} used in climb phase is '
                f'incompatible with the {perf_type} performance model.'
            )

        for inter in seg.interrupts:
            if type(inter) not in inter_allowed:
                raise ValueError(
                    f'Interrupt of type {type(inter)} used in in climb '
                    f'segment, {type(seg)}, is incompatible with the '
                    f'{perf_type} performance model.'
                )
