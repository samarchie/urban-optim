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
from deap import tools, base, creator
import operator

# insert at 0 which is the script path. thus we can import the necessary modules while staying in the same directory
sys.path.insert(0, str(sys.path[0]) + '/src')

warnings.simplefilter("ignore") #Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.

#Set up the logging software so we can track efficieny of the genetic algortihm and see where code breaks
from logger_config import *
logger = logging.getLogger(__name__)

#Import our home-made modules
from initialisation import *
from genetic_algorithm import *
from pareto_plotting import *

#Define the parameters that can be changed by the user

NO_parents = int(input("How many parents? : NO_parents = ")) #number of parents/development plans in each iteration to make
NO_generations = int(input("How many generations? : NO_generations = ")) #how many generations/iterations to complete
prob_crossover = 0.7 #probability of having 2 development plans cross over
prob_mutation = 0.2 #probability of an element in a development plan mutating
prob_mut_indiv = 0.05 #probability of mutating an element d_i within D_i
weightings = np.array([1, 1, 1, 1, 1, 1]) #user defined weightings of each objective function
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
    plot_intialised_data(census, weightings)
    logger.info('f_functions and F-scores plotted and saved')


    ###### PHASE 2 - GENETIC ALGORITHM

    #Initialise and setup the DEAP toolbox of how we store and use our population.
    toolbox = initialise_deap(required_dwellings, density_total, census, NO_parents, prob_mut_indiv, max_density_possible)

    logger.info('Started creating initial population')

    #Create the initial population of NO_parent amount of development plans
    pop = toolbox.population(n=NO_parents)

    #Add the other attributes to the individuals before finding the fitness values
    parents = add_attributes(pop, toolbox, creator, census, max_density_possible)

    #As we are to create 15 differnet pots of objective functions against another objetcive function, we shall have a list wih 15 lists to store the data points
    #             1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    pareto_set = [[], [], [], [], [], [], [], [], [], [], [] ,[] ,[], [] ,[]]

    #For each successful generation, add the parents to the pareto set so that they can be plotted out
    pareto_set = add_to_pareto_set(pareto_set, parents)

    #Create a blank MOPO list where each nested list represents the best case of each objective function (and total F-score) seen
    #           f_tsu  f_cflood  f_rflood f_liq,  f_dist  f_dev,  F-score
    MOPO_List = [[],      [],     [],      [],    [],      [],    []]

    #Update the MOPO list to see if we have any new superior solutions!
    MOPO_List = update_MOPO(MOPO_List, parents, empty=True)

    logger.info('Initial population created and entering GA loop now')



    ###ITERATION PROCEDURE:
    for gen_number in range(1, NO_generations + 1):

        #We must make sure that we follow the rules of the GA method
        assert (prob_crossover + prob_mutation) <= 1.0, ("The sum of the crossover and mutation probabilities must be smaller or equal to 1.0.")

        #In each generation, we need to create NO_parents amount of children! hence, create one at a time.
        children = []
        while len(children) < NO_parents:
            #Generate a random number between 0 and 1, and use this to test HoW we will create a new child!
            op_choice = random.random()

            #Apply cross-over
            if op_choice < prob_crossover:
                #Select two parents via Roulette Selection to create a child
                parent1, parent2 = list(map(toolbox.clone, toolbox.select(individuals=parents, k=2)))
                #Perform a love-making ritual that binds the two parents till death do them part <3
                child = toolbox.mate(parent1, parent2)[0]

            #Apply mutation
            elif op_choice < prob_crossover + prob_mutation:
                #Select 1 parent via Roulette Selection to create a child
                parent = toolbox.clone(toolbox.select(individuals=parents, k=1))
                while type(parent) != creator.Individual:
                    parent = parent[0]

                #The child, straight after birth, recieves a vaccination and this causes autism. They then mutate and well...
                child = toolbox.mutate(parent)[0]

                #Sometimes the returned child is a list of the DEAP class so lets extract it if thats the case
                while type(child) != creator.Individual:
                    child = child[0]

            #Apply reproduction (random parent unchanged)
            else:
                #Select 1 parent via Roulette Selection to create a child. Basically, a random parent is a pedophile and acts to be a kid again.
                child = toolbox.select(individuals=parents, k=1)[0]

            #Update the child attributes with the correct ones
            child.densities = get_densities(child, census)
            child.valid = child_is_good(child, max_density_possible, census)

            # Add the fitness values to the individuals
            # child.fitness = creator.FitnessMulti()
            child.fitness.values = toolbox.evaluate(child)

            #Check to see if it is a bad child, and if it is bad then it is tossed into a volcano as a virgin sacrifice. The good child, however, leads a very happy life and settles down and marries later.
            if child.valid:
                children.append(child)


        #Now we have all the children all ready! lets mix them with the parents and select the fittest ones for the next generation!
        parents[:] = toolbox.select_best(parents + children)

        #For each successful generation, add the parents to the pareto set so that they can be plotted out
        pareto_set = add_to_pareto_set(pareto_set, parents)

        #Update the MOPO list to see if we have any new superior solutions!
        MOPO_List = update_MOPO(MOPO_List, parents)

        logger.info('Generation {} complete'.format(gen_number))

    logger.info('Genetic algorithm complete, exiting for-loop now')



    ########### PHASE 3 - PARETO FRONTS AND OTHER PLOTS

    #Plot the pareto plots so we do our discussion and view the results
    plot_pareto_plots(pareto_set, NO_parents, NO_generations)




    ######### PHASE 4 - ENDING

    print("kachow")




if __name__ == "__main__":
    main()
