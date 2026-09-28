# TODO: Remove this when we migrate to Python 3.14+.
from __future__ import annotations

import operator as op
import tomllib
from pathlib import Path
from typing import Literal

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


class CFR_ROCD_Const_CAS(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_cas']
    """Segment type identifier for TOML input files."""

    cas: float | str
    """Calibrated airspeed of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

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
        traj: Trajectory,
        perf: BasePerformanceModel,
        cfr_data_path: Path | str = 'trajectory/cfr_rocd_data.toml',
    ):
        """Calculate the climb rate prescribed by the US Code of Federal Regulations
        report: Fuel Tank Flammability Method User's Manual (DOT/FAA/AR-05/8).

        Once computed, add to flight rules alongside CAS.
        """
        with open(config.file_location(cfr_data_path), 'rb') as fp:
            raw_cfr = tomllib.load(fp)

        cfr_rocd_model = CFR_ROCD_Table(raw_cfr)

        if not isinstance(self.end_alt, float):
            raise TypeError(
                f'End altitude was passed as a var name ({self.end_alt}) and has not'
                ' been converted to a float by builder.'
            )

        d_alt = self.end_alt - traj.altitude[0]
        rocd = cfr_rocd_model(d_alt, perf.number_of_engines, perf.max_range_km * 1000)
        self.flight_rules[ControlVar.ROCD] = rocd

        # The builder should convert all string variables to floats during its
        # preexecute sequence
        if not isinstance(self.cas, float):
            raise TypeError(
                f'CAS value was passed as a variable name ({self.cas}) and has not'
                ' been converted to a float by builder.'
            )
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
        pass


class CFR_ROCD_Const_Mach(FlightSegmentBase):
    segment_type: Literal['cfr_rocd_const_mach']
    """Segment type identifier for TOML input files"""

    mach: float | str
    """Mach number of the aircraft."""

    roc_pos: bool
    """Whether or not this is a climb or descent. True for climb, False for descent."""

    end_alt: float | str
    """End altitude; either a value in meters or the string name of the variable in the
    ``StandardBuilder``"""

    @model_validator(mode='after')
    def set_next(self):
        self.interrupts.append(
            SegmentEnd(var='altitude', value=self.end_alt, oper=op.gt)
        )

        self.flight_rules[ControlVar.MACH] = self.mach
        return self

    def preexecute(
        self,
        traj: Trajectory,
        perf: BasePerformanceModel,
        cfr_data_path: Path | str = 'trajectory/cfr_rocd_data.toml',
    ):
        """Calculate the climb rate prescribed by the US Code of Federal Regulations
        report: Fuel Tank Flammability Method User's Manual (DOT/FAA/AR-05/8).

        Once computed, add to flight rules.
        """
        with open(config.file_location(cfr_data_path), 'rb') as fp:
            raw_cfr = tomllib.load(fp)

        cfr_rocd_model = CFR_ROCD_Table(raw_cfr)

        d_alt = self.end_alt - traj.altitude[0]
        rocd = cfr_rocd_model(d_alt, perf.number_of_engines, perf.max_range_km * 1000)
        self.flight_rules[ControlVar.ROCD] = rocd

        # The builder should convert all string variables to floats during its
        # preexecute sequence
        if not isinstance(self.mach, float):
            raise TypeError(
                f'Mach value was passed as a variable name ({self.mach}) and has not'
                ' been converted to a float by builder.'
            )
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
        pass


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
        roc = 0  # By definition of constant altitude
        mass = pt.aircraft_mass

        # Take defined distance steps in cruise
        distance = pt.ground_distance + step_size

        state = ACOperationState(
            altitude=alt,
            aircraft_mass=mass,
            rules={
                ControlVar.ROCD: roc,
                ControlVar.MACH: self.mach,
            },
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
        traj: Trajectory,
        perf: BasePerformanceModel,
    ):
        """Add ROCD = 0 and Mach = cruise_mach to flight_rules."""
        self.flight_rules[ControlVar.ROCD] = 0.0

        # The builder should convert all string variables to floats during its
        # preexecute sequence
        if not isinstance(self.mach, float):
            raise TypeError(
                f'Mach value was passed as a variable name ({self.mach}) and has not'
                ' been converted to a float by builder.'
            )
        self.flight_rules[ControlVar.MACH] = self.mach
