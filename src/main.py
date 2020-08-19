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
    boundaries, census_pop, census_houses, infra, hazards, coastal_flood =  get_data()

    #Clip the data if it has not already been clipped
    if not os.path.exists("data/clipped"):
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = clip_to_boundary(boundaries[0], census_pop, census_houses, infra, hazards, coastal_flood)
    else:
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = open_clipped_data(hazards)

    #Merge and process data is it has not already been done
    if not os.path.isfile("data/processed/census_final.shp"):
        if not os.path.exists("data/processed"):
            os.mkdir("data/processed")

        #Want to merge the population and dwelling census Datasets
        merged_census_geo, merged_census_dict = merge_census_data(clipped_census_pop, clipped_houses)

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = add_planning_zones(merged_census_geo, merged_census_dict, boundaries[1], boundaries[0])

        #Update the real parcel size by subtracting the parks and red zones (uninhabitable areas)

        ##TO FUTURE SAM: do we want to clip road widths as well?

        constraints = [boundaries[2], infra[2]] #red zone and parks respectively
        updated_census = apply_constraints(census_zones, constraints)

        #Calulate current density in each parcel
        census_dens = add_density(updated_census)

        #Now want to pre-process everything!
        processed_census = add_f_scores(census_dens, census_pop, clipped_infra, clipped_hazards, clipped_coastal)

    else:
        processed_census = gpd.read_file("data/processed/census_final.shp")

    print(processed_census)
    print("we're all processed dude yayayayaya")

if __name__ == "__main__":
    main()
