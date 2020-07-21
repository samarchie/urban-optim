# -*- coding: utf-8 -*-
"""
Evaluate - 25/05/15
Author: Daniel Caparros-Midwood

Evaluate module for use with the Spatial Optimisation Framework. Used for the London
Case study. Takes a development plan outputted by the Optimisation module and
assesses them against the series of objectives:
1. fheat
2. fflood
3. fdist
4. fsprawl
5. fbrownfield
"""

import numpy as np


def Calc_fheat(London_Dwell_Plan, Data_Folder):
    """ Calculates the average exposure each dwelling is subject to. This is done
    by multiplying the heat hazard array and dwell plan to calculate the aggregate
    heat hazard exposure.
    """

    Heat = (np.loadtxt(Data_Folder+"Heat_Hazard.txt",delimiter=",")).tolist()
    Heat = [float(i) for i in Heat]

    #Calculate the total heat hazard experience by the total dwellings
    HeatRisk = np.multiply(London_Dwell_Plan, Heat)

    # Then divide this by the total number of dwellings in the spatial plan
    HeatRisk_per_Capita = np.sum(HeatRisk)/np.sum(London_Dwell_Plan)

    # Returns the per dwelling heat hazard exposure
    return HeatRisk_per_Capita

def Calc_fflood(London_Dwell_Plan, Data_Folder):
    """ Calculates the average flood risk experienced per dwelling. Multiplies
    the dwell plan by the floodzone array to determine aggregate flood risk then
    divide it by the number of dwellings to

    NOTE: Floodzone 1 in 100 and 1 in 1000 represented by 1 and 0.1 respectively
    """

    Floodzone = (np.loadtxt(Data_Folder+"Floodzone.txt",delimiter=",")).tolist()
    Floodzone = [float(i) for i in Floodzone]

    # Values are 10 and 1 in raster so reducing them
    Floodzone = np.multiply(Floodzone,0.1)

    FloodRisk = np.multiply(London_Dwell_Plan, Floodzone)

    # Calculating a per capita metric as per heat in order to
    FloodRisk_per_Capita = np.sum(FloodRisk)/np.sum(London_Dwell_Plan)

    return FloodRisk_per_Capita

def Calc_fbrownfield(London_DwellPlan, Data_Folder):
    """ Calculate the number of proposed development sites which don't fall on
    brownfield sites
    Target in London Plan is 96%, not enforcing this, will just use it as a
    comparison.
    """

    Brownfield = (np.loadtxt(Data_Folder+"Brownfield.txt",delimiter=",")).tolist()
    Brownfield = [float(i) for i in Brownfield]

    # Calculate the number of proposed sites
    Total_Dev_Sites = np.count_nonzero(London_DwellPlan)

    # Calculate the number of sites which occur on brownfield
    Brownfield_Sites = np.count_nonzero(np.multiply(Brownfield, London_DwellPlan))

    # Calculating this perentage based on the number of dwellings
    Per_Not_Brownfield = (1-(float(Brownfield_Sites)/float(Total_Dev_Sites)))* 100

    return Per_Not_Brownfield

def Calc_fsprawl(London_Dwell_Plan, Data_Folder):
    """ Calculates the number of development sites which fall within the current
    urban area. The number of proposed development sites is calculated by counting
    number of elements in the dwell plan which aren't zeros. We then
    multiply the two arrays. Development corresponding with falling within urban
    areas are retain in urban sites whilst those outside are lost. In this example
    we go from two proposed development sites in Dwell Plan to 1 in Urban Sites
    giving us a fsprawl value of 50%.

    Urban   Dwell Plann   Urban Sites
    [0,     [60,         [0,
    1,   x    0,   ==     0
    1,      100,         100,
    0]       0]           0]

    """

    Urban_Extent = (np.loadtxt(Data_Folder+"Urban.txt",delimiter=",")).tolist()
    Urban_Extent = [float(i) for i in Urban_Extent]

    Total_Dev_Sites = np.count_nonzero(London_Dwell_Plan)
    # Calculate the number of sites within the urban extent
    Urban_Sites = np.count_nonzero(np.multiply(Urban_Extent, London_Dwell_Plan))

    Per_Not_Urban = (1-(float(Urban_Sites)/float(Total_Dev_Sites)))*100

    return Per_Not_Urban

def Calc_fdist(Proposed_Sites, Greenspace_Development):
    """ Function to calculate the average distance between proposed development
    sites. Import a site lookup based on whether greenspace development is
    allowed and lookup their shortest path distance to their closest CBD.
    This value is added to a aggregate score and divided by the number of sites
    Requires the 'Proposed Sites to be in ij format."""

    import Dist_Lookup as Dist_Lookup

    #fdist_values =np.loadtxt('Dist_Lookup.txt', delimiter = ',')

    fdist_values = Dist_Lookup.fdist_lookup

    # Creating an aggregate of the shortest paths
    agg_dist=0
    for dev_site in Proposed_Sites:

        for site in fdist_values:
            if dev_site==site[0]:
                 # Add the shortest path to this site to an aggregate variable
                 # Dividing by 1000 to convert to kilometres
                 agg_dist+= site[1]/1000
    fdist = agg_dist/len(Proposed_Sites)

    return fdist
