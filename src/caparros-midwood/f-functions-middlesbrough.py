# -*- coding: utf-8 -*-
"""
Evaluate 25/05/15
Author: Daniel Caparros-Midwood

The evaluation module receives spatial plans of development and determines the
performance against a series of objectives. Before calling the module, development
plans, 𝐷, in the form [(𝑖,𝑗),(𝑖,𝑗),(𝑖,𝑗)…] are spatial located onto a gridded spatial
plan [[0,0,0…],[0,1,0..],[0,1,1..]] to be directly assessed against the inputted
spatial grids for floodzone etc.

This module forms the evaluation portion of the spatial optimisation framework
for the Middlesbrough Cases Study. It takes development plans plotted against the
stuy area and returns their performance in the following objectives:
1. fheat
2. fflood
3. fdist
4. fsprawl
5. fgreenspace

"""

import numpy as np # Module to handle mathematical calculations
import rasterIO # Module to handle spatial datasets


def Calc_fheat(Spatial_Plan, PopDens, Data_Folder):
    """ Calulcates a heat risk value for the spatial plan. The vulnerability raster
    is updated with the increased population resulting from the proposed spatial
    plans. A comparison is then taken between the original and future heat risk
    by multiplying heat hazard by the current and updated vulnerability dataset.
    """

    Heat_Hazard = rasterIO.readrasterband(rasterIO.opengdalraster(Data_Folder+'Heat_Hazard_100m.tif') ,1)
    Vulnerability = rasterIO.readrasterband(rasterIO.opengdalraster(Data_Folder+'Vulnerability_100m.tif') ,1)

    # Combining the increase in population spatially to current population
    Spatial_Plan_Pop = np.multiply(Spatial_Plan,PopDens)
    Future_Vulnerability = np.add(Spatial_Plan_Pop, Vulnerability)

    # Calculate the current heat risk to calculate the increase associated
    # with this spatial plan
    Current_Risk = np.multiply(Heat_Hazard, Vulnerability)
    Current_Risk_Sum = np.sum(Current_Risk)
    # Calculate future heat risk based on the spatial appropiation of increased
    # population
    Future_Risk = np.multiply(Heat_Hazard, Future_Vulnerability)
    Future_Risk_Sum = np.sum(Future_Risk)
    # Objective function is the difference between the risks
    fheat = Future_Risk_Sum - Current_Risk_Sum

    return fheat

def Calc_fflood(Spatial_Plan, Dwellings, Data_Folder):
        """ Calculates the aggregate flood risk to dwellings
        """

        Flood_Hazard = rasterIO.readrasterband(rasterIO.opengdalraster(Data_Folder+'Floodzone_100m.tif') ,1)

        Vulnerability = np.multiply(Spatial_Plan, Dwellings) # Assing the number of dwellings to each cell
        fflood = float(np.sum(np.multiply(Vulnerability, Flood_Hazard)))

        return fflood

def Calc_fdist(Dev_Plan, Data_Folder):
    """ Calculates the average distance of proposed development to a CBD.
    A pre-processing module calculates the shortest path distance from all possible
    development sites which is stored as a fdist lookup. Based on a proposed development
    the function lookups the shortests paths for proposed development sites
    and returns an average
    """

    import fdist_lookup
    fdist_values = fdist_lookup.fdist_lookup

    # Creating an aggregate of the shortest paths
    agg_dist=0
    for dev_site in Dev_Plan:
        # Find its corresponding feature in the fdist lookup list
        for site in fdist_values:
            if dev_site==site[0]:
                # Add the shortest path to this site to an aggregate variable
                agg_dist+= site[1]
    fdist = agg_dist/len(Dev_Plan)
    return fdist

def Calc_fsprawl(Spatial_Plan, Data_Folder):
    """ Calculates the numbers of proposed developed sites which fall within
    the defined urban extent. This is compared to the total number to calculate
    a percentage outside the urban extent
    """

    Urban_Extent = rasterIO.readrasterband(rasterIO.opengdalraster(Data_Folder+'Urban_Extent_100m.tif') ,1)

    # Calculates total numberof development sites
    No_Sites = float(np.sum(Spatial_Plan))

    # Calculate the number of sites which remain once its multiplied by the urban extent measure
    # Urban areas are 1 and others are 0 so dev sites outside it are lost in the calculation
    No_Sites_WithinUrban = float(np.sum(np.multiply(Spatial_Plan, Urban_Extent))/100)

    # We then use the difference between the number of development sites and
    # those which correspond with the urban extent to calculate a %
    fsprawl = (1 - (No_Sites_WithinUrban/No_Sites))*100

    return fsprawl
