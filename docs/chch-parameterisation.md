## Implementation of Objective Functions Used in the Analysis for Ōtautahi Christchurch

Sam Archie & Jamie Fleming, supervised by Tom Logan; (2020)

<br>

#### Description and parameterisation of each objective function used

| Objective name | Description | Parameterisation |
|----------------|-------------|------------------|
| f<sub>tsu</sub> | Minimise exposure to inundation from a tsunami | Normalised by the maximum inundation depth in any SA |
| f<sub>cflood</sub> | Minimise exposure to a 1 in 100-year coastal flooding surge. Includes increased exposure due to sea-level rise in increments of 0.1 meters, up to 3 meters | Normalised by the maximum inundation depth in any SA |
| f<sub>rflood</sub> | Minimise exposure to future river flooding risk | Data did not provide inundation depths, just where it was affected by the flooding. As a result, the objective function returns a binary result |
| f<sub>liq</sub> | Minimise exposure to future liquefaction risk | Assigned a value in the range 0-1 based on liquefaction susceptibility and judgement |
| f<sub>dis</sub>t | Minimise the distance of new development to town centres to minimise travel | Normalised by the maximum distance for the centroid of any SA from a town centre |
| f<sub>dev</sub> | Minimise expansion of urban sprawl in rural zones | Objective function scores each SA based on the percentage of the area which is zoned be developed on (residential, mixed) |
