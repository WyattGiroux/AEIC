# TODO: Remove this when we move to Python 3.14+.
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from AEIC.config import config
from AEIC.missions import Mission
from AEIC.performance.models import PerformanceModel
from AEIC.units import (
    FEET_TO_METERS,
    NAUTICAL_MILES_TO_METERS,
)
from AEIC.weather import Weather

from .. import GroundTrack, Trajectory, TrajectorySchedule
from .base import Builder, Context, Options


@dataclass
class StandardOptions:
    """Additional options for the standard trajectory builder."""

    altitude_step: float = 1000 * FEET_TO_METERS
    """Altitude step to use in climb and descent phases (m)."""

    cruise_step: float = 125 * NAUTICAL_MILES_TO_METERS
    """Ground distance step to use in cruise phase (m)."""

    fuel_LHV: float = 43.8e6
    """Lower heating value of the fuel used (J/kg)."""


class StandardContext(Context):
    class AdjustmentFunction(Protocol):
        """Protocol for context adjustment functions.

        An adjustment function takes in the context, mission, performance model
        possibly additional optional keyword arguments and returns a float
        value."""

        def __call__(
            self,
            context: StandardContext,
            mission: Mission,
            performance: PerformanceModel,
            trajectory_schedule: TrajectorySchedule,
            **kwargs,
        ) -> float: ...

    # A context adjustment is either an adjustment function, a fixed float
    # value, or None (in which case no adjustment is applied and the behavior
    # falls back to the standard legacy trajectory builder behavior).
    ContextAdjustment = AdjustmentFunction | float | None

    def __init__(
        self,
        builder: StandardBuilder,
        ac_performance: PerformanceModel,
        mission: Mission,
        trajectory_schedule: TrajectorySchedule,
        starting_mass: float | None,
        start_altitude: ContextAdjustment = None,
        cruise_start_altitude: ContextAdjustment = None,
        end_altitude: ContextAdjustment = None,
        reserve_fuel: ContextAdjustment = None,
        divert_distance: ContextAdjustment = None,
        hold_time: ContextAdjustment = None,
    ):
        """Adjustment parameters (a "simple" adjustment is one that takes no
        additional arguments beyond the context, mission and performance
        model):

        - `start_altitude`: Simple adjustment for mission start altitude,
          which defaults to 3000' above departure airport altitude if not
          provided.

        - `cruise_start_altitude`: Simple adjustment for cruise altitude, which
           defaults to 7000' below aircraft operating ceiling if not provided.

        - `end_altitude`: Simple adjustment for descent end altitude,
           which defaults to 3000' above arrival airport altitude if not
           provided.

        - `descent_distance`: Simple adjustment for descent distance, which
           defaults to a value based on the difference between cruise altitude
           and descent end altitude if not provided.

        - `reserve_fuel`: Adjustment for reserve fuel mass, which defaults to
           5% of total fuel mass if not provided (additional parameter:
           `fuel_mass`, total fuel mass consumed based on approximate flight
           time and nominal fuel flow).

        - `divert_distance`: Adjustment for diversion distance, which defaults
          to 200 NM if flight time is over 3 hours and 100 NM if flight time is
          under 3 hours if not provided (additional parameter: `approx_time`,
          approximate flight time based on distance and nominal cruise speed).

        - `hold_time`: Adjustment for hold time, which defaults to 30 minutes
          if flight time is over 3 hours and 45 minutes if flight time is under
          3 hours if not provided (additional parameter: `approx_time`,
          approximate flight time based on distance and nominal cruise speed).
        """
        # raise NotImplementedError('StandardContext is not yet implemented.')

        ground_track = GroundTrack.great_circle(
            mission.origin_position.location,
            mission.destination_position.location,
            allow_overstep=True,
        )

        # Climb defined as starting 3000' above airport (adjustable).
        if start_altitude is None:
            self.start_altitude = (
                mission.origin_position.altitude + 3000.0 * FEET_TO_METERS
            )
        else:
            self.start_altitude = self.apply_adjustment(
                start_altitude, mission, ac_performance, trajectory_schedule
            )

        if self.start_altitude >= ac_performance.maximum_altitude:
            self.start_altitude = mission.origin_position.altitude

        # Cruise altitude is the operating ceiling - 7000 feet (adjustable).
        if cruise_start_altitude is None:
            self.cruise_start_altitude = (
                ac_performance.maximum_altitude - 7000.0 * FEET_TO_METERS
            )
        else:
            self.cruise_start_altitude = self.apply_adjustment(
                cruise_start_altitude, mission, ac_performance, trajectory_schedule
            )

        # Ensure cruise altitude is above the starting altitude.
        if self.cruise_start_altitude < self.start_altitude:
            self.cruise_start_altitude = self.start_altitude

        # Prevent flying above aircraft ceiling.
        if self.cruise_start_altitude > ac_performance.maximum_altitude:
            self.cruise_start_altitude = ac_performance.maximum_altitude

        # Set descent altitude based on 3000' above arrival airport altitude;
        # clamp to aircraft operating ceiling if needed (adjustable).
        if end_altitude is None:
            self.end_altitude = (
                mission.destination_position.altitude + 3000.0 * FEET_TO_METERS
            )
        else:
            self.end_altitude = self.apply_adjustment(
                end_altitude, mission, ac_performance
            )

        if self.end_altitude >= ac_performance.maximum_altitude:
            self.end_altitude = ac_performance.maximum_altitude

        if self.cruise_start_altitude < self.start_altitude:
            raise ValueError(
                "Initial trajectory point should not be higher "
                "than start of cruise point"
            )

        # Initialize weather regridding when requested.
        self.weather: Weather | None = None
        if builder.options.use_weather:
            self.weather = Weather(
                data_dir=config.weather.weather_data_dir,
                file_resolution=config.weather.file_resolution,
                data_resolution=config.weather.data_resolution,
                file_format=config.weather.file_format,
            )

        # Save reserve fuel, divert distance and hold time adjustments for use
        # in starting mass calculation.
        self.reserve_fuel = reserve_fuel
        self.divert_distance = divert_distance
        self.hold_time = hold_time

        # Pass information to base context class constructor.
        super().__init__(
            builder,
            ac_performance,
            mission,
            ground_track,
            initial_altitude=self.clm_start_altitude,
            starting_mass=starting_mass,
        )

    def apply_adjustment(
        self,
        adjustment: ContextAdjustment,
        mission: Mission,
        performance: PerformanceModel,
        trajectory_schedule: TrajectorySchedule,
        **kwargs,
    ) -> float:
        """Helper function to apply a context adjustment."""
        if adjustment is None:
            raise RuntimeError('Attempting to apply an empty ContextAdjustment.')
        elif isinstance(adjustment, Callable):
            return adjustment(self, mission, performance, trajectory_schedule, **kwargs)
        else:
            return adjustment


class StandardBuilder(Builder):
    """."""

    CONTEXT_CLASS = StandardContext

    def __init__(
        self,
        options: Options = Options(),
        standard_options: StandardOptions = StandardOptions(),
    ):
        super().__init__(options)

        # Altitude step to use in climb and descent phases of flight.
        self.altitude_step = standard_options.altitude_step

        # Ground distance step to use in cruise phase.
        self.cruise_step = standard_options.cruise_step

        self.fuel_LHV = standard_options.fuel_LHV

    def fly_iteration(self) -> tuple[Trajectory, float]: ...

    def calc_starting_mass(self) -> float: ...

    def climb(self, traj: Trajectory) -> None: ...

    def cruise(self, traj: Trajectory) -> None: ...

    def descent(self, traj: Trajectory) -> None: ...
