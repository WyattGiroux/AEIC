from unittest.mock import Mock

import pytest

from AEIC.performance.types import Performance
from AEIC.trajectories import GroundTrack
from AEIC.trajectories.segments import ControlVar, FlightSegment
from tests.utils import make_test_trajectory


def test_evaluate_constant_perf(sample_missions):
    """Ensure Const_Alt_Const_Mach passes a state with ROCD=0 and MACH set to
    the configured value when calling ac_performance.evaluate(), and that the
    performance object returned (constant) is propagated to _update_distance_step.
    """
    # Create segment via FlightSegment loader to ensure proper model construction
    seg = FlightSegment.load_from_dict(
        {"segment_type": "const_alt_const_mach", "mach": 0.78}
    )

    mission = sample_missions[0]

    # Make a minimal trajectory with one point so make_point(-1) works
    traj = make_test_trajectory(1, seed=1)
    traj._extensible = True

    # Mock performance model: evaluate returns a constant perf object
    constant_perf = Performance(true_airspeed=100, rate_of_climb=0, fuel_flow=0.1)
    ac_perf = Mock()
    ac_perf.evaluate = Mock(return_value=constant_perf)

    def _ground_track(mission):
        return GroundTrack.great_circle(
            mission.origin_position.location,
            mission.destination_position.location,
            allow_overstep=True,
        )

    ground_track = _ground_track(mission)

    # Call the segment fly step
    seg._fly_step(
        traj=traj,
        ac_performance=ac_perf,
        ground_track=ground_track,
        step_size=1000.0,
        is_backwards=False,
        weather=None,
        mission=mission,
    )

    # Check evaluate was called exactly once
    ac_perf.evaluate.assert_called_once()

    # Inspect the 'state' argument passed to evaluate
    _, kwargs = ac_perf.evaluate.call_args
    assert "state" in kwargs
    state = kwargs["state"]

    # Ensure rules include ROCD=0 and MACH equal to the segment's mach
    assert ControlVar.ROCD in state.rules
    assert ControlVar.MACH in state.rules
    assert state.rules[ControlVar.ROCD] == 0
    assert state.rules[ControlVar.MACH] == 0.78

    alts = traj.altitude
    mass = traj.aircraft_mass

    # Make sure we only have two points
    assert len(alts) == 2

    # No altitude change
    assert alts[-1] - alts[0] == 0

    # Make sure mass changed as intended
    dt = traj.flight_time[-1] - traj.flight_time[0]
    assert mass[0] - mass[-1] == pytest.approx(0.1 * dt)
