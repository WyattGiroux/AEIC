from AEIC.config import config
from AEIC.trajectories import TrajectorySchedule
from AEIC.trajectories.segments import (
    CFR_ROCD_Const_CAS,
    CFR_ROCD_Const_Mach,
    # Const_Alt_Const_Mach,
    SegmentInterruptBase,
)


def test_vertical_traj_initialization():
    """Ensure TrajectorySchedule can read a basic trajectory definition"""

    traj_schedule = TrajectorySchedule(
        config.file_location('trajectory/standard_trajectory.toml')
    )

    # Make sure climb segments loaded correctly
    clm = traj_schedule.climb
    assert len(clm) == 2
    assert isinstance(clm[0], CFR_ROCD_Const_CAS)
    assert isinstance(clm[1], CFR_ROCD_Const_Mach)

    # Check that the end condition on altitude was automatically created
    clm_interrupts = clm[0].interrupts
    assert len(clm_interrupts) == 1
    assert clm_interrupts[0].code == SegmentInterruptBase.InterruptCode.NEXT
    assert clm_interrupts[0].var == 'altitude'


def test_traj_schedule_validation_success():
    """Successful loading and validation of the schedule"""
    pass
