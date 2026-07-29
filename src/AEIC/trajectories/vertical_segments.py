from AEIC.performance.models import BasePerformanceModel


def parse_trajectory_segments(
    raw_traj,
    perf_model: BasePerformanceModel,
):
    """Parser to take the toml version of a trajectory definition and convert it to
    ordered lists representing climb, cruise, and desccent.

    Arguments:
        raw_traj (dict): Dictionary representation of the trajectory read in from the
            specified trajectory toml file.

    Returns:
        climb_segments (list[FlightSegment]): Ordered list of flight rules for climb
        cruise_segments (list[FlightSegment]): Ordered list of flight rules for cruise
        descent_segments (list[FlightSegment]): Ordered list of flight rules for descent
    """


# class FlightRule:
#     """Encodes a rule for constraining aircraft performance as a variable name,
#     target value, and comparison operator (chosen from either 'set', or the list of
#     standard binary comparison operators). If 'set' is chosen, v

#     Can be called directly (the following returns True):

#         rule = FlightRule('altitude', '35000', '>=')
#         rule(37000, 35000)

#     Arguments:
#         - name (str): Variable name, should be the exact variable name from the
#         trajectory fieldset being used.
#         - val (float): Value to be set/evaluated against.

#     """
#     _ops = {
#         '==': op.eq,
#         '!=': op.ne,
#         '<':  op.lt,
#         '<=': op.le,
#         '>':  op.gt,
#         '>=': op.ge,
#     }

#     def __init__(self, name:str, val:float, oper:str):
#         self.name = name
#         self.val = val
#         if oper not in self._ops:
#             raise KeyError(f'Invalid Operator: {oper}')

#         self.oper = self._ops[oper]

#     def __call__(self, traj:Trajectory) -> bool:
#         """ Allow evaluation by directly passing the

#         """
#         curr_value = getattr(traj, self.name)[-1]
#         return self.oper(curr_value, self.val)

#     def __repr__(self):
#         return f"FlightRule({self.name!r}, {self.op!r}, {self.value!r})"
