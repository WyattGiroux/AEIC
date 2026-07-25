# Trajectories

Trajectories in AEIC are defined as the operation profile of the aircraft
starting at 914 meters (3000 feet) above the departure airport and ending 914
meters above the arrival airport. All operations below 914 meters relative to
the departure/arrival airport are classified as LTO operations and are
(optionally) represented using ICAO Annex 16 Volume II time-in-modes. AEIC
assumes that a negligible amount of fuel is burned during these operations.

AEIC currently only supports a trajectory simulation method which is very
similar to the legacy ([AEIC v2](https://zenodo.org/records/6461767))
trajectory model. In the future, support for additional trajectory models will
be added. Possible additions include more dynamics-driven non-trapezoidal
trajectories, trajectories closer to real flight tracks based on
[ADS-B](https://www.adsbexchange.com/) data, and optimized (horzontal,
vertical, speed) trajectories.

```{toctree}
:maxdepth: 1

trajectory_data.md
trajectory_builders.md
trajectory_stores.md
constraining_ac_perf.md
```

## Custom Vertical Trajectories
```{eval-rst}
.. WARNING::
    Custom vertical trajectories are currently under active development and
    should not be used.
```
AEIC defines the vertical trajectory path of an aircraft as a series of
flight segments which each have:
 * Two rules defining how the aircraft performs over that segment.
 * End-conditions for that segment.
 * A list of conditions which, if met, trigger dynamic modification of the trajectory.
