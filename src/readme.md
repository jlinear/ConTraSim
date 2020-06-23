# Features and Usage

map_builder.py:

## Netconvert related options:

### input
--osm-file (opt)
DONE!

### output
--output.original-names (df: False) --> True
--output.street-names (df: False) --> True
--parking-output ??
DONE!

### projection
TBD

### Processing
--lefthand (df: False)  --> TF
--geometry.remove (df:False) --> True
--roundabouts.guess (df: True)
DONE!

### Building defaults
TBD

### Traffic Lights (Tls building)
--tls.guess-signals (df: False) --> True
--tls.discard-simple (df: False) --> True
--tls.join (df: False) --> True
--tls.default-type,actuated (df: static)
TODO: explore further options at <https://sumo.dlr.de/docs/NETCONVERT.html#tls_building>

### Ramp guessing
--ramps.guess (df: False) --> True
DONE!

### Edge Removal
TBD

### Unregulated nodes
TBD

### Junctions
--junctions.join (df: False) --> True
--junctions.corner-detail, 5 (df: 5) --> stay 5
DONE!

### Pedestrian
Options in this field mainly consider whether sidewalk and crossings should be added for pedestrian when building the map.
Guessing based on speed is not included, walking area option is not considered, either.

--sidewalks.guess (df: False) --> True
--crossings.guess (df: False) --> True
DONE!

### Bicycle
Similar to pedestrian as above
--bikelanes.guess
DONE!

### Railway
Will not be considered in this tool, and if used, the default value will be applied.
DONE!

### Formats


### Report
-v/--verbose (df: False) --> True
DONE!

### Random Number
set a static value if there is a need


## polyconvert options
This option is only used for better visulization, and not directly related to simulation output.

-v,--osm.keep-full-type

