# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import operator as op
import tomllib
from typing import TYPE_CHECKING, Literal

import numpy as np
from pydantic import model_validator

from AEIC.config import config
from AEIC.missions import Mission
from AEIC.performance.models import BasePerformanceModel
from AEIC.trajectories.segments.segment_base import (
    ACOperationState,
    ControlVar,
    FlightSegmentBase,
    SegmentEnd,
)
from AEIC.trajectories.trajectory import Trajectory
from AEIC.types import CFR_ROCD_Table
from AEIC.weather import Weather

from .. import GroundTrack

if TYPE_CHECKING:
    from AEIC.trajectories.builders import StandardBuilder


class CFR_ROCD_Const_CAS(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_cas']
    """Segment type identifier for TOML input files."""

    cas: float | str
    """Calibrated airspeed of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    start_alt: float | str
    """Starting altitude for the climb/descent in meters or string name of var."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    @model_validator(mode='after')
    def initialize(self):
        self.interrupts.append(
            SegmentEnd(var='altitude', value=self.end_alt, oper=op.gt)
        )
        return self

    def preexecute(
        self,
        builder: StandardBuilder,
    ):
        """Calculate the climb rate prescribed by the US Code of Federal Regulations
        report: Fuel Tank Flammability Method User's Manual (DOT/FAA/AR-05/8).

        Once computed, add to flight rules alongside CAS.
        """
        # TODO add variable for data location to config
        with open(config.file_location('trajectory/cfr_rocd_data.toml'), 'rb') as fp:
            raw_cfr = tomllib.load(fp)

        cfr_rocd_model = CFR_ROCD_Table(raw_cfr)

        # Fetch float values from builder if necessary
        if not isinstance(self.end_alt, float):
            self.end_alt = self.search_builder_params(builder, self.end_alt)

        if not isinstance(self.start_alt, float):
            self.start_alt = self.search_builder_params(builder, self.start_alt)

        if not isinstance(self.cas, float):
            self.cas = self.search_builder_params(builder, self.cas)

        perf = builder.ac_performance
        frac_max_range = builder.ground_track.total_distance / (
            perf.max_range_km * 1000
        )

        d_alt = self.end_alt - self.start_alt
        rocd = cfr_rocd_model(d_alt, perf.number_of_engines, frac_max_range)

        # Add flight rules
        self.flight_rules[ControlVar.ROCD] = rocd
        self.flight_rules[ControlVar.CAS] = self.cas

    def _fly_step(
        self,
        traj: Trajectory,
        ac_performance: BasePerformanceModel,
        ground_track: GroundTrack,
        step_size: float,
        is_backwards: bool,
        weather: Weather | None,
        mission: Mission,
    ):
        pt = traj.make_point(-1)
        alt = pt.altitude
        mass = pt.aircraft_mass

        # Take defined altitude steps
        new_alt = pt.altitude + step_size

        state = ACOperationState(
            altitude=alt,
            aircraft_mass=mass,
            rules=self.flight_rules,
        )

        # Obtain the current performance of the aircraft
        perf = ac_performance.evaluate(
            state=state,
            rules=None,  # Leftover from legacy implementation
        )

        horizontal_airspeed = np.sqrt(perf.true_airspeed**2 - perf.rate_of_climb**2)

        self._update_altitude_step(
            traj=traj,
            pt=pt,
            new_alt=new_alt,
            horizontal_airspeed=horizontal_airspeed,
            perf=perf,
            ground_track=ground_track,
            is_backwards=is_backwards,
            weather=weather,
            mission=mission,
        )


class CFR_ROCD_Const_Mach(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_mach']
    """Segment type identifier for TOML input files"""

    mach: float | str
    """Mach number of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    start_alt: float | str
    """Starting altitude for the climb/descent in meters or string name of var."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    @model_validator(mode='after')
    def set_next(self):
        self.interrupts.append(
            SegmentEnd(var='altitude', value=self.end_alt, oper=op.gt)
        )
        return self

    def preexecute(
        self,
        builder: StandardBuilder,
    ):
        """Calculate the climb rate prescribed by the US Code of Federal Regulations
        report: Fuel Tank Flammability Method User's Manual (DOT/FAA/AR-05/8).

        Once computed, add to flight rules.
        """
        # TODO add variable for data location to config
        with open(config.file_location('trajectory/cfr_rocd_data.toml'), 'rb') as fp:
            raw_cfr = tomllib.load(fp)

        cfr_rocd_model = CFR_ROCD_Table(raw_cfr)

        # Fetch float values from builder if necessary
        if not isinstance(self.end_alt, float):
            self.end_alt = self.search_builder_params(builder, self.end_alt)

        if not isinstance(self.start_alt, float):
            self.start_alt = self.search_builder_params(builder, self.start_alt)

        if not isinstance(self.mach, float):
            self.mach = self.search_builder_params(builder, self.mach)

        perf = builder.ac_performance
        frac_max_range = builder.ground_track.total_distance / (
            perf.max_range_km * 1000
        )

        d_alt = self.end_alt - self.start_alt
        rocd = cfr_rocd_model(d_alt, perf.number_of_engines, frac_max_range)

        # Add flight rules
        self.flight_rules[ControlVar.ROCD] = rocd
        self.flight_rules[ControlVar.MACH] = self.mach

    def _fly_step(
        self,
        traj: Trajectory,
        ac_performance: BasePerformanceModel,
        ground_track: GroundTrack,
        step_size: float,
        is_backwards: bool,
        weather: Weather | None,
        mission: Mission,
    ):
        pt = traj.make_point(-1)
        alt = pt.altitude
        mass = pt.aircraft_mass

        # Take defined altitude steps
        new_alt = pt.altitude + step_size

        state = ACOperationState(
            altitude=alt,
            aircraft_mass=mass,
            rules=self.flight_rules,
        )

        # Obtain the current performance of the aircraft
        perf = ac_performance.evaluate(
            state=state,
            rules=None,  # Leftover from legacy implementation
        )

        horizontal_airspeed = np.sqrt(perf.true_airspeed**2 - perf.rate_of_climb**2)

        self._update_altitude_step(
            traj=traj,
            pt=pt,
            new_alt=new_alt,
            horizontal_airspeed=horizontal_airspeed,
            perf=perf,
            ground_track=ground_track,
            is_backwards=is_backwards,
            weather=weather,
            mission=mission,
        )


class Const_Alt_Const_Mach(FlightSegmentBase):
    segment_type: Literal['const_alt_const_mach']
    """Segment type identifier for TOML input files"""

    mach: float | str
    """Mach number of the aircraft."""

    def _fly_step(
        self,
        traj: Trajectory,
        ac_performance: BasePerformanceModel,
        ground_track: GroundTrack,
        step_size: float,
        is_backwards: bool,
        weather: Weather | None,
        mission: Mission,
    ):
        pt = traj.make_point(-1)
        alt = pt.altitude
        mass = pt.aircraft_mass

        # Take defined distance steps in cruise
        distance = pt.ground_distance + step_size

        state = ACOperationState(
            altitude=alt,
            aircraft_mass=mass,
            rules=self.flight_rules,
        )

        # Obtain the current performance of the aircraft
        perf = ac_performance.evaluate(
            state=state,
            rules=None,  # Leftover from legacy implementation
        )

        self._update_distance_step(
            traj=traj,
            pt=pt,
            distance=distance,
            horizontal_airspeed=perf.true_airspeed,
            perf=perf,
            ground_track=ground_track,
            is_backwards=is_backwards,
            weather=weather,
            mission=mission,
        )

    def preexecute(
        self,
        builder: StandardBuilder,
    ):
        """Add ROCD = 0 and Mach = cruise_mach to flight_rules."""
        if not isinstance(self.mach, float):
            self.mach = self.search_builder_params(builder, self.mach)

        self.flight_rules[ControlVar.MACH] = self.mach
        self.flight_rules[ControlVar.ROCD] = 0.0
