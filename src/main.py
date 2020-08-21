# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call
upon any other functions it needs to do the genetic algorthm!

Good luck
"""

import os
import geopandas as gpd

#Import our home-made modules
from src.initialisation import *


def main():
    """Now this is where the magic happens!"""
    #Phase 1: initialisation

    #Get data from the user
    boundaries, constraints, census, hazards, coastal_flood, distances = get_data()

    #Clip the data if it has not already been clipped
    if not os.path.exists("data/clipped"):
        clipped_census, clipped_hazards, clipped_coastal = clip_to_boundary(boundaries[0], census, hazards, coastal_flood)

    clipped_census, clipped_hazards, clipped_coastal = open_clipped_data(hazards)

    #Merge and process data is it has not already been done
    if not os.path.isfile("data/processed/census_final.shp"):
        if not os.path.exists("data/processed"):
            os.mkdir("data/processed")

        #Add the District Plan Zones that can be built on to the constraints list
        constraints = update_constraints(non_building_zones, constraints, boundaries[1])

        #Update the real parcel size by subtracting the parks and red zones (uninhabitable areas)
        constrained_census = apply_constraints(clipped_census, constraints)

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = add_planning_zones(constrained_census, boundaries)

        #Calulate current density in each parcel
        census_dens = add_density(census_zones)

        #Now want to pre-process everything!
        processed_census = add_f_scores(census_dens, census, clipped_hazards, clipped_coastal)

    else:
        processed_census = gpd.read_file("data/processed/census_final.shp")

    print(processed_census)
    print("we're all processed dude yayayayaya")

if __name__ == "__main__":
    main()
