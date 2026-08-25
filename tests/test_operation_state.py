import pytest

from AEIC.trajectories.segments import ACOperationState, ControlVar


def test_overdefiend_state():
    with pytest.raises(ValueError):
        _ = ACOperationState(
            altitude=5000,
            aircraft_mass=1e5,
            rules={
                ControlVar.THROTTLE_FRAC: 0.5,
                ControlVar.CAS: 168.0,
                ControlVar.ROCD: 1.0,
            },
        )
