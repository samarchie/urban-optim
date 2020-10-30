## Multi-Criterion Spatial Optimization of Christchurch's Urban Development

Sam Archie & Jamie Fleming, supervised by Tom Logan; (2020)

{% include button.html button_name="Report" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/report.pdf" %}

## Background

The sustainable development of cities has recently been identified as an important way for us to adapt to and help solve climate change. In response, the National Policy Statement on Urban Development requires urban-planners to design future urban areas in New Zealand strategically for the next generations, primarily through intensification of existing residential areas. Local authorities are currently unequipped to assess areas for future development through a quantitive lens, whilst considering the tradeoffs between multiple planning objectives. This paper continues the development of a multi-criteria spatial optimisation framework from previous researchers through the use of a genetic algorithm. The framework is applied to the case study of Ōtautahi Christchurch to identify areas of priority for urban intensification, to aid decision-makers where to guide future growth whilst taking into account multiple hazard adaption and sustainability objectives.

The objectives of this study are to locate appropriate areas for urban development in Ōtautahi Christchurch based on the method used by Caparros-Midwood. The focus of the research is to design an open-ended multi-objective spatial optimisation program that can be applied to any given city with a set of hazards and constraints. The results of the multi-objective spatial optimisation case study of Ōtautahi Christchurch are recommended to form part of an evidence base to showcase and deliver risk management of proposed developments to Christchurch City Council urban planners and other relevant stakeholders.

**This genetic algorithm package aims to find an optimal, or a series of optimal, scenarios that are better for a range of attributes (known as objective functions). Although the algorithm is currently programmed for Ōtautahi Christchurch, it is possible for this code to be adapted for other cities in New Zealand.**


## Planning Goals Implemented

The objective functions for the Christchurch optimisation study defines the following:
1. f<sub>tsu</sub>: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Minimise exposure to inundation from a tsunami
2. f<sub>cflood</sub>: &nbsp;&nbsp;Minimise exposure to a 1 in 100-year coastal flooding surge, including sea level rise
3. f<sub>rflood</sub>: &nbsp;&nbsp;Minimise exposure to future river flooding risk
4. f<sub>liq</sub>: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Minimise exposure to future liquefaction risk
5. f<sub>dist</sub>: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Minimise the distance of new development to town centres to minimise travel
6. f<sub>dev</sub>: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Minimise expansion of urban sprawl in rural zones

The implementation (parameterisation) of each GIS layer to a quantitive function can be found [here](URL) or by clicking the "Parameterisation". Moreover, the source of each data layer to form the objectives are accessible by clicking the 'Data Sources' button below.

{% include button.html button_name="Parameterisation" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/chch-parameterisation" %} {% include button.html button_name="Data Sources" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/data-sources" %}

<br>

## Results

The results of the analysis are presented and further discussed in the report, *Multi-Criterion Spatial Optimization of Christchurch’s Urban Development* by Sam Archie (@samarchie) and Jamie Fleming(@Fleming171) with supervision from Tom Logan (@tommlogan).

High-quality figures and plots are reproduced on this website by clicking the "Figures" button.

Interactive 3D plots are also accessible by clicking the appropiate

{% include button.html button_name="Figures" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/chch-sample-figures" %}


{% include button.html button_name="3D Visualisation of Existing Density" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/chch-existing-density.html" %} {% include button.html button_name="3D Visualisation of Existing Density" button_class="outline-primary" url="https://samarchie.github.io/urban-optim/chch-results-density.html" %}


[Link](url) and ![Image](src)
```
