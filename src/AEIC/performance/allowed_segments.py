# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

from AEIC.trajectories.segments import (
    CFR_ROCD_Const_CAS,
    CFR_ROCD_Const_Mach,
    Const_Alt_Const_Mach,
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

ALLOWED_INTERRUPTS = {}


# ALLOWED_INTERRUPTS will need to be added to ensure trajectory schedules are valid
# before simulation begins.
