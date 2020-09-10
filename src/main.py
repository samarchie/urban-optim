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
import warnings
import matplotlib.pyplot as plt
import numpy as np
import random

warnings.simplefilter("ignore") #Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.

#Import our home-made modules
from src.initialisation import *
from src.genetic_algorithm import *

#Define the parameters that can be changed by the user
NO_parents = 5 #number of parents/development plans in each iteration to make
generations = 5 #how many generations/iterations to complete
prob_crossover = 0.7 #probability of having 2 development plans cross over
prob_mutation = 0.2 #probability of an element in a development plan mutating
weightings = [1, 1, 1, 1, 1, 1] #user defined weightings of each objective function
required_dwellings = 20000 #amount of required dwellings over entire region
density_total = 10 #Define what are acceptable maximum densities for new areas (in dwelling/hecatres)


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
        constrained_census = apply_constraints(clipped_census, constraints, boundaries[0])

        #Add the District Planning Zone in the Census GeoDataFrame
        census_zones = add_planning_zones(constrained_census, boundaries[1])

        #Calulate current density in each parcel
        census_dens = add_density(census_zones)

        #Now want to pre-process everything!
        processed_census = add_f_scores(census_dens, clipped_hazards, clipped_coastal, distances)

        #Clean the data properties up!
        cleaned_census = clean_processed_data(processed_census)

        #Take the user weightings and find the F score for each statistical area!
        census_final = apply_weightings(cleaned_census, weightings)

    else:
        census_final = gpd.read_file("data/processed/census_final.shp")

    #Plot the processed census data and check the objective functions are working as expected!
    plot_intialised_data(census_final)


    ###### PHASE 2 - GENETIC ALGORITHM

    #Create an initial set of devlopment plans so that we can start the optimisation somewhere
    development_plans = create_initial_development_plans(NO_parents, required_dwellings, density_total, census_final)

    #Calculate how well each randomised development plan actually does compared to the objective functions, and also overall.
    development_plans = evaluate_development_plans(development_plans, census_final)

    #Here's a little section to plot out each of the initial randomised development plans
    # for development_plan in development_plans:
    #     np_list = np.asarray(development_plan[1])
    #     census_final[np_list != 0].plot()
    # plt.show()


    #ITERATION PROCEDURE:
    for generation_number in range(0, generations):
        #We must perform these modifications to a set amount of iterations, called generations.

        #We must modify and randomise each development plan generated initially.
        for development_plan_index in range(0, NO_parents):
            #Generate a random number between 0 and 1, and use this to test if we shall crossover two solutions in a development plan.
            random_number = random.random()

            if random_number <= prob_crossover:
                #Then we shall crossover two development plans
                development_plans = apply_crossover(development_plan_index, development_plans)

                #Update the densities of the development plans as the dwelling counts have changed in some statistical areas
                development_plans = update_densities(development_plans, census_final)

                #Then we want to check that the new densities do not exceed the sustainable urban density limit specified by the user


            elif random_number <= prob_mutation + prob_crossover:
                #Then we didnt crossover the solutions and we can mutate the development plan!
                development_plan = apply_mutation(development_plan_index, development_plans)

                #Update the densities of the development plans as the dwelling counts have changed in some statistical areas
                development_plans = update_densities(development_plans, census_final)

            # If the two randomisations dont occur, then the plan are not updated and kept as is.


if __name__ == "__main__":
    main()

# code.interact(local=locals())
