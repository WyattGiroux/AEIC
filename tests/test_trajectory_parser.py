from typing import Literal

from AEIC.config import config
from AEIC.trajectories import TrajectorySchedule

# from AEIC.trajectories.segments import (
#     CFR_ROCD_Const_CAS,
#     CFR_ROCD_Const_Mach,
#     Const_Alt_Const_Mach,
# )


def test_vertical_traj_initialization():
    """Ensure TrajectorySchedule can read a basic trajectory definition"""

    traj_schedule = TrajectorySchedule(
        config.file_location('trajectory/standard_trajectory.toml')
    )

    # Ensure all phases are present
    assert 'climb' in traj_schedule
    assert 'cruise' in traj_schedule
    assert 'descent' in traj_schedule

    # Make sure climb segments loaded correctly
    clm = traj_schedule['climb']
    assert len(clm) == 2
    assert clm[0].segment_type == Literal['cfr_rocd_const_cas']
    assert clm[1].segment_type == Literal['cfr_rocd_const_mach']


def test_traj_schedule_validation_success():
    """Successful loading and validation of the schedule"""
    pass
