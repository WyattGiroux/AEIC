# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import numpy as np
import pandas as pd


class CFR_ROCD_Table:
    """Representation of the climb/descent rates used in FAA/AR/05/8 as a function of
    number of engines and fraction of max range being flown.
    """

    def __init__(self, raw_cfr):
        self.descent_low = raw_cfr['descent']['rod_low']
        self.descent_high = raw_cfr['descent']['rod_high']
        self.descent_breakpoint = raw_cfr['descent']['breakpoint_altitude']

        self.data = pd.DataFrame(
            data=raw_cfr['climb']['data'], columns=raw_cfr['climb']['cols']
        )

    def __call__(self, dalt: float, n_eng: int, frac_max_range: float):
        # TODO Figure out how to incorporate the high/low descent rates dynamically in a
        # single segment
        if dalt < 0:
            return self.descent_high

        if frac_max_range > 1:
            raise ValueError(
                'Fraction of maximum range must be between 0 and 1 inclusive. Was given'
                f' {frac_max_range}.'
            )

        if n_eng < 2 or n_eng > 4:
            raise ValueError(
                'CFR method for climb rates only accepts 2, 3, and 4 engine aircraft.'
                f' Was given {n_eng}.'
            )

        # Range fraction can be 0, .2, .4, ... 1.0
        # To clamp 0-1 to these, first shift decimal and half range such that 0 -> 0,
        # 1 -> 0.2, 2 -> 0.4, ..., 5 -> 1.0
        range_filter_value = np.floor(frac_max_range * 10 / 2) / 10 * 2

        data_eng_filter = self.data['n_eng'] == n_eng
        range_filter = np.isclose(self.data['frac_max_range'], range_filter_value)

        total_filter = data_eng_filter & range_filter
        climb_time = self.data[total_filter]['climb_time'].values[0]

        return dalt / climb_time
