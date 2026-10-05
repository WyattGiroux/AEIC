import tomllib

import pytest

from AEIC.config import config
from AEIC.types import CFR_ROCD_Table


@pytest.fixture
def cfr_table():
    with open(config.file_location('trajectory/cfr_rocd_data.toml'), 'rb') as fp:
        raw_cfr = tomllib.load(fp)

    return CFR_ROCD_Table(raw_cfr=raw_cfr)


def test_get_climb_rate(cfr_table):
    n_eng = 2
    dalt = 6000
    frac_max_range = 0.33

    climb_rate = cfr_table(dalt, n_eng, frac_max_range)

    assert climb_rate == pytest.approx(5.0)

    n_eng = 2
    dalt = 6000
    frac_max_range = 0.9

    climb_rate = cfr_table(dalt, n_eng, frac_max_range)
    assert climb_rate == pytest.approx(2.85714285714285)
