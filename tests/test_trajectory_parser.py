from AEIC.config import config
from AEIC.trajectories import TrajectorySchedule


def test_vertical_traj_initialization():
    """Ensure TrajectorySchedule can read a basic trajectory definition"""

    _ = TrajectorySchedule(config.file_location('trajectories/sample_trajectory.toml'))


def test_traj_schedule_validation_success():
    """Successful loading and validation of the schedule"""
    pass
