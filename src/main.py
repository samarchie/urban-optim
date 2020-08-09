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
#Import our home-made modules
import src.initialise as init


def main():
    """Now this is where the magic happens!"""
    #Phase 1: initialisation

    #Get data from the user
    boundaries, census_pop, census_houses, infra, hazards, coastal_flood =  init.get_data()

    #Clip the data if it has not already been clipped
    ### MAKE SURE TO ADD A NOT IN THE IF STATEMENT BELOW WHEN DONE!!!
    if not os.path.exists("data/clipped"):
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal, clipped_zones = init.clip_to_boundary(boundaries[0], census_pop, census_houses, infra, hazards, coastal_flood, boundaries[1])
    else:
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal, clipped_zones = init.open_clipped_data(hazards)

    #Merge and process data is it has not already been done
    ### MAKE SURE TO ADD A NOT IN THE IF STATEMENT BELOW WHEN DONE!!!
    if not os.path.isfile("data/processed/census.shp"):
        os.mkdir("data/processed")
        #Want to merge the population and dwelling census Datasets
        merged_census = init.merge_census_data(clipped_census_pop, clipped_houses)

        #Calulate current density in each parcel
        census_dens = init.add_density(merged_census)

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = init.add_planning_zones(census_dens, boundaries[1])

        #Now want to pre-process everything!
        processed_census = init.add_f_scores(census_zones, census_pop, clipped_infra, clipped_hazards, clipped_coastal)
    else:
        processed_census = gpd.read_file("data/processed/census.shp")

    print(processed_census)

if __name__ == "__main__":
    main()
