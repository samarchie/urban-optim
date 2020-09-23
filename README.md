## Multi-Criterion Spatial Optimization of Christchurch's Urban Development

Sam Archie & Jamie Fleming, supervised by Tom Logan; (2020)

The District Plan guides where and how future urban development can occur. In its solicitation, the council released analysis showing five potential scenarios: baseline, suburban centres, centralization, natural hazards, and greenfield. The expectation is that the preferred scenario will represent a blend of these.

However, there are some things we cannot choose. Natural hazards are going to impact us under any of these scenarios. What will the effect of these hazards be on the other scenarios? Similarly, what are the vehicle emissions resulting from each scenario proposed?

The objectives of this study are to locate appropriate areas for urban development in Ōtautahi Christchurch based on the method used by Caparros-Midwood. The focus of the research is to design an open-ended multiobjective spatial optimisation program that can be applied to any given city with a set of hazards and constraints. The results of the multi-objective spatial optimisation case study of Ōtautahi Christchurch are recommended to form part of an evidence base to showcase and deliver risk management of proposed developments to Christchurch City Council urban planners and other relevant stakeholders.

##### This genetic algorithm package aims to find an optimal, or a series of optimal, scenarios that are better for a range of attributes (known as objective functions). Although the algorithm is currently programmed for Ōtautahi Christchurch, it is possible for this code to be adapted for other cities in New Zealand.

The objective functions for the Christchurch optimisation study defines the following:
1. f_tsu
2. f_cflood
3. f_rflood
4. f_liq
5. f_dist
6. f_dev

#### Modules required:
* [x] geopandas
* [x] matplotlib
* [x] gdal
* [x] rasterIO
* [x] descartes
* [x] rasterstats
