# Performance Model Minimum Requirements

In order to interface with the standard (non-legacy) AEIC trajectory builder,
{py:class}`StandardBuilder <AEIC.trajectories.builders.standard.StandardBuilder>`,
a user-provided performance model must at minimum have the following fields:

## Common Fields
These are the fields that all performance models must share. Additional fields can be provided in addition to these, but all the following fields **must** be present when using the {py:class}`StandardBuilder <AEIC.trajectories.builders.standard.StandardBuilder>`.

### Metadata

 * `aircraft_name` identifies the aircraft being modeled. Prefer short codes
   (e.g. `"B738"`)
 * `aircraft_class` is a rough grouping of size/use case. Can be `narrow`, `wide`,
   `small`, or `freight`.
 * `ISA_offset` is the temperature offset (in K) used when calculating standard atmospheric
   properties.
 * `maximum_altitude_ft` is the service ceiling of the aircraft in feet.
 * `maximum_payload_kg` is the maximum payload of the aircraft in kilograms.
 * `number_of_engines` is the number of engines.
 * `APU_name` is the name of the auxilliary power unit. If set to `None`, APU emissions
   will not be calculated.
 * `max_range_km` is the maximum range of the aircraft in kilometers.

### Speeds

 * `cruise_mach` is the average cruise Mach number (typically in the 0.78-0.85 range).

### Landing/Takeoff Emissions Data

 * `source` is the source of LTO emissions data. Can be `"EDB"` or `"self"`.

#### `EDB` Fields
 * `ICAO_UID`: the unique identifier of the engine in the EASA Engine Emisisons Databank.

```{eval-rst}
.. NOTE::
    Currently only specifications for the EDB LTO data fields are provided here. If you wish to manually input the data, follow the format used by :code:`AEIC.data.performance.sample_performance_model.toml`
```

## Model-Specific Fields
This section will vary from model to model and is where the actual performance data lives. While different performance models will store/parse data differently, in order to use the standard trajectory a model must provide a querying method that accepts altitude, mass, and two flight rules (stored as a dictionary with variable as key and value as entry) and returns a fuel flow rate.
