from typing import Literal

ALLOWED_SEGMENTS = {
    Literal('legacy'): [
        Literal('bada_ptf_climb'),
        Literal('bada_ptf_cruise'),
        Literal('bada_ptf_descent'),
    ]
}
