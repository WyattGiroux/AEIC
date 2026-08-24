from typing import Literal

from .models import (
    LegacyPerformanceModel,
    # TASOPTPerformanceModel,
)

ALLOWED_SEGMENTS = {
    LegacyPerformanceModel: [
        Literal('bada_ptf_climb'),
        Literal('bada_ptf_cruise'),
        Literal('bada_ptf_descent'),
    ]
}

ALLOWED_INTERRUPTS = {}

# ALLOWED_INTERRUPTS will need to be added to ensure trajectory schedules are valid
# before simulation begins.
