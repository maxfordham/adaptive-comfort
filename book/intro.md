# Welcome to Adaptive Comfort!

This package allows us to assess IES building projects to make sure that the rooms pass the necessary CIBSE criteria.

## Workflow

The process of how the script obtains the report:

```{mermaid}
    flowchart TD
        subgraph P1 [IES]
            A[Obtain weather and room data from IES API]
        end
        subgraph P2 [Adaptive Comfort]
         B[Calculate Operative Temperature, Maximum Acceptable<br> Temperature, and delta Ts] --> C[Calculate TM52 Criteria for each room] --> D[Output report to excel]
        end
    P1 --> P2
```

"IES" is another Max Fordham python package to obtain the IES data necessary to perform the criteria calculations. 

```{note}
The IES package is NOT used to perform the criteria calculation. It is purely for getting data out of the IES application.
```

"Adaptive Comfort" is this package, and it is used to calculate and perform the necessary criteria for both TM52 and TM59. This package requires the data from IES's API to run the calculations and test the criteria.

This package contains CIBSE's TM52 calculation (and soon the TM59 calculation):

{doc}`calculation`

