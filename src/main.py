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
import src.initialise as init


def main():
    """Now this is where the magic happens!"""
    #Phase 1: initialisation

    #Get data from the user
    boundaries, census_pop, census_houses, infra, hazards, coastal_flood =  init.get_data()

    #Clip the data if it has not already been clipped
    if not os.path.exists("data/clipped"):
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = init.clip_to_boundary(boundaries[0], census_pop, census_houses, infra, hazards, coastal_flood)
    else:
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = init.open_clipped_data(hazards)

    #Merge and process data is it has not already been done
    if not os.path.isfile("data/processed/census.shp"):
        if not os.path.exists("data/processed"):
            os.mkdir("data/processed")

        #Want to merge the population and dwelling census Datasets
        merged_census_geo, merged_census_dict = init.merge_census_data(clipped_census_pop, clipped_houses)

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = init.add_planning_zones(merged_census_geo, merged_census_dict, boundaries[1])

        #Calulate current density in each parcel
        census_dens = init.add_density(census_zones)

        #Now want to pre-process everything!
        processed_census = init.add_f_scores(census_dens, census_pop, clipped_infra, clipped_hazards, clipped_coastal)
    else:
        processed_census = gpd.read_file("data/processed/census.shp")

    print(processed_census)

if __name__ == "__main__":
    main()
