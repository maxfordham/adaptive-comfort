# Welcome to Adaptive Comfort!

This package assesses the thermal comfort of a space within a building against the criterion defined in CIBSE TM52 and TM59.  

## Inputs
- Air temperature of the rooms
- Mean radiant temperature of the rooms
- Elevated air speed within rooms (as default the calculation is run at every air speed)
- External dry bulb temperature
- Annual occupancy profile

## Outputs 
- TM52/TM59 pass or fail for each criterion for each room

The calculation is performed in Python where the inputs for our tests are from IES using the Virtual Environment API.

The calculation can also be completed independently of the IES Virtual Environment API provided that the inputs data objects are populated appropriately.
