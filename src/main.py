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
    boundary, census_pop, census_houses, infra, hazards, coastal_flood =  init.get_data()

    #Clip the data if it has not already been clipped
    ### MAKE SURE TO ADD A NOT IN THE IF STATEMENT BELOW WHEN DONE!!!
    if not os.path.exists("data/clipped"):
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = init.clip_to_boundary(boundary, census_pop, census_houses, infra, hazards, coastal_flood)
    else:
        clipped_census_pop, clipped_houses, clipped_infra, clipped_hazards, clipped_coastal = init.open_clipped_data(hazards)

    #Want to merge the population and dwelling census Datasets
    merged_census = init.merge_census_shapefiles(clipped_census_pop, clipped_houses)

    #Now want to pre-process everything!
    processed_census = init.add_f_scores(merged_census, census_pop, clipped_infra, clipped_hazards, clipped_coastal)

    print(processed_census.head())

if __name__ == "__main__":
    main()
