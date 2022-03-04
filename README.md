# Welcome to Adaptive Comfort!

This package assesses the thermal comfort of a space within a building against the Criterion defined in CIBSE TM52 and TM59.  

## Inputs
- air temperature of the rooms
- mean radiant temperature of the rooms
- elevated air speed within rooms (as default the calculation is run at every air speed)
- external dry bulb temperature
- annual occupancy profile

## Outputs: 
- TM52/TM59 pass or fail for each criterion for each room

The calculation is done in python; the inputs for this calculation can be extracted from IES using the VEscripts API, as described here: __[MXF_IES_UserGuide_VEScripts_014](https://wiki.maxfordham.com/pub/Main/MXFIESUSERGUIDEVESCRIPTS/MXF_IES_UserGuide_VEScripts_014.pdf)__. 

The calculation could also be done independently of IES, provided that the inputs are given in the appropriate format. 

