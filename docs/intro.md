# Welcome to Adaptive Comfort!

This package assesses the thermal comfort of a space within a building against the Criterion defined in CIBSE TM52 {cite}`tm52_report` and TM59 {cite}`tm59_report`.  

## Inputs
- air temperature of the rooms
- radiant temperature of the rooms
- wind speed within rooms (as default the calculation is run at every air speed)
- external dry bulb temperature
- annual occupancy profile

## Outputs: 
- TM52/TM59 pass or fail for each criterion for each room

The calculation is done in python; the inputs for this calculation can be extracted from IES using the VEscripts API, as described here: __[MXF_IES_UserGuide_VEScripts_014](https://wiki.maxfordham.com/pub/Main/MXFIESUSERGUIDEVESCRIPTS/MXF_IES_UserGuide_VEScripts_014.pdf)__. 

The calculation could also be done inpependently of IES, provided that the inputs are given in the appropriate format. 

## Workflow

The process of how the script obtains the report:

```{mermaid
    flowchart TD
        subgraph P1 [VEscripts]
            A[export_tm52_results.py<br>Obtain weather and room data from IES API]
        end
        subgraph P2 [adaptive_comfort]
         B[Calculate: Operative Temperature, <br>Maximum Acceptable<br> Temperature, <br> delta Ts] --> C[Calculate TM52 Criteria for each room] --> D[Output report to excel]
        end
    P1 --> P2
```

Once in VEScripts, run export_tm52_results.py. This obtains the data through the IES API and then the adaptive_comfort python package is called to perform the calculations and see whether the spaces pass the criteria. This is then all output into an excel spreadsheet.

```{bibliography}
:filter: docname in docnames
```