from IPython.display import Markdown, display

display(Markdown("README.md"))


*References: {cite}`a-tm52_report` and TM59 {cite}`a-tm59_report`*

## Workflow

The process of how the script obtains the report:

```{mermaid}
    flowchart TD
        subgraph P1 [VEscripts]
            A[export_tm52_results.py<br>Obtain weather and room data from IES API]
        end
        subgraph P2 [adaptive_comfort]
         B[Calculate: Operative Temperature, <br>Maximum Acceptable<br> Temperature, <br> delta Ts] --> C[Calculate TM52 Criteria for each room] --> D[Output report to excel]
        end
    P1 --> P2
```

When in the VEScript editor in IES VE, open the script folder and run export_tm52_results.py. This script obtains the data through the IES API and then calls the adaptive_comfort python package to perform the calculations. The calculations will see whether the spaces pass the criteria successfully or not. All this information is then output into an excel spreadsheet.

---

```{bibliography}
:filter: docname in docnames
:labelprefix: A
:keyprefix: a-
```
