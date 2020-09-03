# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call upon any other functions it needs to do the genetic algorthm!

Good luck
"""

import os
import geopandas as gpd

#Import our home-made modules
from src.initialisation import *
from src.genetic_algorithm import *

#Define the parameters that can be changed by the user
acceptable_dwelling_densities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] #Define what are acceptable densities for new areas (in dwelling/hecatres)
NO_parents = 5 #number of parents/development plans in each iteration to make
generations = 5 #how many generations/iterations to complete
prob_crossover = 0.7 #probability of having 2 development plans cross over
prob_mutation = 0.2 #probability of a development plan mutating
weightings = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6] #weightings of each objective function
required_dwellings = 20000 #amount of required dwellings over entire region



def main():
    """Now this is where the magic happens!"""
    ####### PHASE 1 - INTIALISATION

    #Get data from the user
    boundaries, constraints, census, hazards, coastal_flood, distances = get_data()

    #Clip the data if it has not already been clipped
    if not os.path.isfile("data/clipped/census.shp"):
        if not os.path.exists("data/clipped"):
            os.mkdir("data/clipped")

        clipped_census, clipped_hazards, clipped_coastal = clip_to_boundary(boundaries[0], census, hazards, coastal_flood)

    clipped_census, clipped_hazards, clipped_coastal = open_clipped_data(hazards)

    #Process data if it has not already been done
    if not os.path.isfile("data/processed/census_final.shp"):
        if not os.path.exists("data/processed"):
            os.mkdir("data/processed")

        #Add the District Plan Zones that cant be built on to the constraints list
        constraints = update_constraints(constraints, boundaries[1])

        #Update the real parcel size by subtracting the parks and red zones (uninhabitable areas)
        constrained_census = apply_constraints(clipped_census, constraints)

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = add_planning_zones(constrained_census, boundaries[1])

        #Calulate current density in each parcel
        census_dens = add_density(census_zones)

        #Now want to pre-process everything!
        processed_census = add_f_scores(census_dens, clipped_hazards, clipped_coastal, distances)

        #Clean the data properties up!
        cleaned_data = clean_processed_data(processed_census)

        #Take the user weightings and find the F score for each statistical area!
        census_final = add_F_scores(cleaned_data, weightings)

    else:
        census_final = gpd.read_file("data/processed/census_final.shp")

    #Plot the processed census data and check the objective functions are working as expected!
    plot_intialised_data(census_final)


    ###### PHASE 2 - GENETIC ALGORITHM

    development_plans, addition_of_dwellings = create_initial_development_plans(NO_parents, required_dwellings, acceptable_dwelling_densities, census_final)


if __name__ == "__main__":
    main()
