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
import sys

# insert at 0 which is the script path. thus we can import the necessary modules while staying in the same directory
sys.path.insert(0, str(sys.path[0]) + '/src')

warnings.simplefilter("ignore") #Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.

#Set up the logging software so we can track efficieny of the genetic algortihm and see where code breaks
from logger_config import *
logger = logging.getLogger(__name__)

#Import our home-made modules
from initialisation import *
from genetic_algorithm import *
from non_dom_sorting import *
from pareto_plotting import *

#Define the parameters that can be changed by the user
NO_parents = 10 #number of parents/development plans in each iteration to make
generations = 1 #how many generations/iterations to complete
prob_crossover = 0.7 #probability of having 2 development plans cross over
prob_mutation = 0.2 #probability of an element in a development plan mutating
prob_mut_indiv = 0.05 #probability of mutating an element d_i within D_i
weightings = [1, 1, 1, 1, 1, 1] #user defined weightings of each objective function
required_dwellings = 20000 #amount of required dwellings over entire region
density_total = 10.0 #Define what are acceptable maximum densities for new areas (in dwelling/hecatres)
max_density_possible = 11.0 #As our crossover/mutation seciton will change densities, we need an upper bound that


def main():
    """Now this is where the magic happens!"""
    ####### PHASE 1 - INTIALISATION

    #Get data from the user
    boundaries, constraints, census_raw, hazards, coastal_flood, distances = get_data()

    #Clip the data if it has not already been clipped
    if not os.path.isfile("data/clipped/census.shp"):
        if not os.path.exists("data/clipped"):
            os.mkdir("data/clipped")

        clipped_census, clipped_hazards, clipped_coastal = clip_to_boundary(boundaries[0], census_raw, hazards, coastal_flood)

    clipped_census, clipped_hazards, clipped_coastal = open_clipped_data(hazards)
    logger.info('Clipping complete')

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
        census = apply_weightings(cleaned_census, weightings)

    else:
        census = gpd.read_file("data/processed/census_final.shp")

    logger.info('Processing/initialisation complete')

    # Plot the processed census data and check the objective functions are working as expected!
    plot_intialised_data(census)
    logger.info('f_functions and F-scores plotted and saved')


    ###### PHASE 2 - GENETIC ALGORITHM

    #Create an initial set of devlopment plans so that we can start the optimisation somewhere
    development_plans = create_initial_development_plans(NO_parents, required_dwellings, density_total, census)

    #Calculate how well each randomised development plan actually does compared to the objective functions, and also overall.
    development_plans = evaluate_development_plans(development_plans, census)

    #Establish a master list that retians that parents at each iteration. Evidently, the 0th place is for the initial parents we just created
    parents_at_each_generation = [development_plans]
    logger.info('Initial plans created and entering GA now')


    #ITERATION PROCEDURE:
    for generation_number in range(0, generations):
        #We must perform these modifications to a set amount of iterations, called generations.

        #Grab the parents (which are the successfulf children from last iteration) and use them to make the new children
        parents = parents_at_each_generation[-1][:]

        #In each generation, we need to create NO_parents amount of children! hence, create one at a time.
        children = []

        while len(children) < NO_parents:
            #Generate a random number between 0 and 1, and use this to test HOW we will create a new child!
            random_number = random.random()

            if random_number <= prob_crossover:
                #Select two parents to create 2 children via Roulette Selection
                selected_parents = do_roulette_selection(parents, 2)

                #Then we shall crossover two development plans and get some children!
                children_created = apply_crossover(selected_parents)

                children_created = list(children_created)

            elif random_number <= prob_mutation + prob_crossover:

                #Select one parents to create 1 children via Roulette Selection
                selected_parent = do_roulette_selection(parents, 1)

                #Then we shall create child by mutating one parent
                children_created = apply_mutation(selected_parent, prob_mut_indiv)

            else:
                # If the two randomisations dont occur, then the plan are not updated and kept as is from the original dveelopment plan list. But to keep the same format as the other children, only take the dwelling additons list
                children_created = [parents[len(children)][2][:]]

            #Update the densities of the development plans as the dwelling counts have changed in some statistical areas
            children_plans = update_densities(children_created, census)

            #Do some constraint handling, as the density cant be larger than the sustainable limit set by the user so we must check each new child to make sure they are okay
            for child in children_plans:

                #Test if they meet the constraints of density limits
                if child_is_good(child, max_density_possible, census):
                    #Give the child a filler value thta means nothing, just because thats how the evaluate_development_plans module is coded up and there must be something in the 0th spot.
                    child.insert(0, "filler value")

                    #Want to calculate the F-scores
                    evaluated_children = evaluate_development_plans([child], census)
                    evaluated_child = evaluated_children[0]

                    #make sure we aren't adding a child to the list if we have already reached the limit. This case may exists when doing crossover is done but only 1 child is required
                    if len(children) < NO_parents:
                        #Delete that stupid filler value we added before
                        evaluated_child.pop(0)
                        #And insert the correct child index value!
                        evaluated_child.insert(0, len(children))
                        #Then add to children lists
                        children.append(evaluated_child)

                #If the child does not meet the constraints of the density limit, then it is not carried on and is not used any further. basically it is aborted and another child will be made as the list is stll under the NO_parents threshold.

        #Now we have all the children we require, and we must rank them against the parents!
        parents_and_children = children + parents

        #Do non dominated sorting to figure out the champions between the children and the parents
        ######NEED TO ASK JAMIE HOW TO USE HIS SORT FUNCTION. KINDA NEEDS TO INPUT EVERYTHING NOT JUST F-FUNCTIONS
        new_parents = Sort(parents_and_children)

        #Update the MOPO list to see if we have any new superior solutions!
        MOPO_List = [(-1, []), (-1, []), (-1, []), (-1, []), (-1, []), (-1, []), (-1, [])]
        MOPO_List = MOPO_update(MOPO_List, new_parents)

        #Save the successful children in the master list so that they can be used for the next iteration!
        parents_at_each_generation.append(new_parents)

        logger.info('Generation {} complete'.format(generation_number))

    logger.info('Genetic algorithm complete, exiting for-loop now')

    ########### PHASE 3 - PARETO PLOTS

    #As we are to create 15 differnet pots of objective functions against another objetcive function, we shall have a list wih 15 lists to store the data points
    #             1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    pareto_set = [[], [], [], [], [], [], [], [], [], [], [] ,[] ,[], [] ,[]]

    #For each successful generation, add the parents to the pareto set so that they can be plotted out
    for parents in parents_at_each_generation:
        pareto_set = add_to_pareto_set(pareto_set, parents)

    logger.info('Pareto set has been updated with all parents')

    #Plot the pareto plots so we do our discussion and view the results
    plot_pareto_fronts(pareto_set)




if __name__ == "__main__":
    main()
