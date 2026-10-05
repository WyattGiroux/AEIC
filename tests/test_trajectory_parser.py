import pytest

from AEIC.config import config
from AEIC.performance.allowed_segments import validate_trajectory_schedule
from AEIC.performance.models import LegacyPerformanceModel, TASOPTPerformanceModel
from AEIC.trajectories import TrajectorySchedule
from AEIC.trajectories.builders.standard import StandardBuilder, StandardContext
from AEIC.trajectories.segments import (
    CFR_ROCD_Const_CAS,
    CFR_ROCD_Const_Mach,
    # Const_Alt_Const_Mach,
    SegmentInterruptBase,
)
from AEIC.types import AircraftClass


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


def test_traj_schedule_validation(trajectory_schedule):
    """Successful loading and validation of the schedule"""
    validate_trajectory_schedule(trajectory_schedule, TASOPTPerformanceModel)


def test_traj_schedule_validation_fail(trajectory_schedule):
    """Successful loading and validation of the schedule"""
    with pytest.raises(ValueError):
        validate_trajectory_schedule(trajectory_schedule, LegacyPerformanceModel)


def test_context_validation(trajectory_schedule, sample_missions):
    """This test replicates the behavior of StandardBuilder.fly()'s call to create the
    context class, where trajectory schedule validation takes place.
    """
    # Create mocked performance object to test without a functional performance model
    perf = TASOPTPerformanceModel(
        aircraft_name='test',
        aircraft_class=AircraftClass.NARROW,
        maximum_altitude_ft=40000,
        maximum_payload_kg=1000000,
        number_of_engines=2,
        apu_name=None,
        speeds=None,
        lto_performance=None,
        model_type='TASOPT',
        max_range_km=5000,
        cruise_mach=0.8,
    )

    # Initialize the context via the builder
    builder = StandardBuilder()
    ctx = StandardContext(
        builder=builder,
        ac_performance=perf,
        mission=sample_missions[0],
        trajectory_schedule=trajectory_schedule,
        starting_mass=None,
    )
    builder.ctx = ctx
