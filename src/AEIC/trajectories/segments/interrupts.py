from AEIC.trajectories.segments.segment_base import SegmentEnd, SegmentInterrupt


class InterruptDefinitions:
    class End_Altitude(SegmentEnd):
        def __init__(self, end_alt: float):
            super().__init__(var='altitude', value=end_alt, oper='>=')

    class Min_CL_Step_Climb(SegmentInterrupt):
        def __init__(self, min_cl, max_cl):
            # Use max_cl to define end condition for new_climb
            new_climb = ...
            new_cruise = ...

            super().__init__(
                var='CL',
                value=min_cl,
                oper='<=',
                code=SegmentInterrupt.InterruptCode.INSERT_NEXT,
                insert_segments=[
                    new_climb,
                    new_cruise,
                ],
            )
