# TM52 Calculation

## Code

Flowchart:

flowchart TD
    Start --> Stop


## Mathematics

1. Calculate The Operative Temperature
    Calculate operative temperature for each room that we want to analyse.
    It'll do this for each air speed. *Reference: See CIBSE Guide A, Equation 1.2, Part 1.2.2*

    $$
        T_{op} = \frac{T_{a}\sqrt{10v} + T_{r}}{1 + \sqrt{10v}}
    $$

    where $T_{op}$ is the operative room temperature ($^\circ C$),

    $T_{a}$ is the indoor air temperature $(^\circ C)$,

    $T_{r}$ is the mean radiant temperature $(^\circ C)$,

    and $v$ is the summer (elevated) air speed $(ms^{-1})$.

2. Calculate The Maximum Acceptable Temperature
    Calculate the maximum acceptable temperature for each room that we want to analyse.
    

    It'll do this for each air speed. *Reference: See CIBSE Guide A, Equation 1.2, Part 1.2.2*

3. Calculate Delta T
    Calculates changes in temperature for each room between the operative temperature and the maximum
    acceptable temperature. *Reference: See CIBSE TM52: 2013, Page 13, Equation 9, Section 6.1.2*

4. Run through the TM52 criteria
    Criterion one 
        No room can have delta T equal or excede the threshold (1 kelvin) during occupied hours for more than 3 percent of the 
        total occupied hours. *Reference: See CIBSE TM52: 2013, Page 13, Section 6.1.2a*
    Criterion two
        No room can have a daily weight greater than the threshold (6) where the daily weight is calculated from the reporting intervals
        within occupied hours. *Reference: See CIBSE TM52: 2013, Page 14, Section 6.1.2b*
    Criterion three 
        No room, at any point, can have a reading where delta T excedes the threshold (4 kelvin). *Reference: See CIBSE TM52: 2013, Page 14, Section 6.1.2c*

5. Merge Data Frames
    Merges the data frames for project information, criterion percentage definitions, and the results for each 
    air speed.

6. Output To Excel
    Outputs the dataframes to an excel spreadsheet in the project location.