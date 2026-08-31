# Performance Model Minimum Requirements

In order to interface with the standard (non-legacy) AEIC trajectory builder,
{py:class}`StandardBuilder <AEIC.trajectories.builders.standard.StandardBuilder>`,
a user-provided performance model must at minimum have the following fields:

## Common Fields
These are the fields that all performance models must share. Additional fields can be provided in addition to these, but all the following fields **must** be present when using the {py:class}`StandardBuilder <AEIC.trajectories.builders.standard.StandardBuilder>`.

### Metadata
 * `model_degree` (`int`) is the number of flight rules (e.g. CAS = 250 kt) supported by the model. Minimum is 0 (e.g. BADA `.ptf` file), maximum is 2 (e.g. TASOPT).
 * `aircraft_name` (`str`) identifies the aircraft being modeled. Prefer short codes
   (e.g. `"B738"`)
 * `aircraft_class` (`str`) is a rough grouping of size/use case. Can be `narrow`, `wide`,
   `small`, or `freight`.
 * `ISA_offset` (`float`) is the temperature offset (in K) used when calculating standard atmospheric
   properties.
 * `maximum_altitude_ft` (`float`) is the service ceiling of the aircraft in feet.
 * `maximum_payload_kg` (`float`) is the maximum payload of the aircraft in kilograms.
 * `number_of_engines` (`int`) is the number of engines.
 * `APU_name` (`str`) is the name of the auxilliary power unit. If set to `None`, APU emissions
   will not be calculated.
 * `max_range_km` (`float`) is the maximum range of the aircraft in kilometers.
 * `cruise_mach` is the average cruise Mach number (typically in the 0.78-0.85 range).
 * `source` is the source of LTO emissions data. Can be `"EDB"` or `"self"`.
 * `ICAO_UID`: the unique identifier of the engine in the EASA Engine Emisisons Databank.

```{eval-rst}
.. NOTE::
    Currently only specifications for the EDB LTO data fields are provided here. If you wish to manually input the data, follow the format used by :code:`AEIC.data.performance.sample_performance_model.toml`
```

## Performance Evaluation
Whether or not the model is tabulated or functional, every performance model must have an `evaluate` method:

```{eval-rst}
.. autofunction:: AEIC.performance.models.BasePerformanceModel
   :members:
```
