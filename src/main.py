# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call upon any other functions it needs to do the genetic algorthm!

Good luck
"""

import os, warnings, random, sys, operator, array, math
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from deap import tools, base, creator

# insert at 0 which is the script path. thus we can import the necessary modules while staying in the same directory
sys.path.insert(0, str(sys.path[0]) + '/src')

warnings.simplefilter("ignore") #Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.

#Set up the logging software so we can track efficieny of the genetic algortihm and see where code breaks
from logger_config import *
logger = logging.getLogger(__name__)

#Import our home-made modules
from initialisation import *
from genetic_algorithm import *
from plotting import *

######Get the algorithm parameters that can be changed by the user########

NO_parents = int(input("How many parents? : NO_parents = ")) #number of parents/development plans in each iteration to make
NO_generations = int(input("How many generations? : NO_generations = ")) #how many generations/iterations to complete

prob_crossover = 0.7 #probability of having 2 development plans cross over
prob_mutation = 0.2 #probability of an element in a development plan mutating
prob_mut_indiv = 0.05 #probability of mutating an element d_i within D_i

assert (prob_crossover + prob_mutation) <= 1.0, ("The sum of the crossover and mutation probabilities must be smaller or equal to 1.0.")

weightings = [] #user defined weightings of each objective function
i= True
while i:
    input_split = input("give weightings for Tsunami hazard, Coastal Flooding hazard, River Flooding hazard, Liquefaction hazard, minimising urban Sprawl and prioritising Council zoning. Should be six numbers separated by commas: ").split(",")
    for item in input_split:
        weightings.append(float(item))
    if len(weightings) == 6:
        i = False
    else:
        print("u dumb dumb. need six numbers in format 'a, b, c, d, e, f' ")
weighting_scheme = input("Give a name to your weighting scheme: weighting_scheme = ") # So we can name the plots for each scheme

required_dwellings = int(input("How many dwellings? : required_dwellings = ")) #amount of required dwellings over entire region
dwelling_scheme = input("Give a name to your dwelling scheme: dwelling_scheme = ") # So we can name the plots for each scheme

scheme = weighting_scheme + ', ' + dwelling_scheme

density_total = []
input_split = input("Enter up to 8 acceptable densities, seperated with a comma, in units of dwellings per hectare: ").split(',') #Define what are acceptable maximum densities for new areas (in dwelling/hecatres)
for item in input_split:
    density_total.append(float(item))

# density_total = [42, 55, 66, 83, 92, 111, 133] # Default numbers
max_density_possible = int(input("Maximum possible density, in units of dwellings per hectare? : max_density_possible = ")) #To limit how many dwellings can be added to any one SA

assert max_density_possible >= max(density_total), ("The maximum permissible sustainable urban density must be larger than all of the allowable sustainbale urban densities.")

step_size = input("How often (in generations) shall the spatial plans be plotted? : step_size = ")
when_to_plot = range(0, NO_generations + 1, int(step_size)) #specify [start, end, spacing] when we should plot out what generations to show the spatial variations of the parents (eg best locations)


def main():
    """Now this is where the magic happens!"""
    ####### PHASE 1 - INTIALISATION

    #Get data from the user
    boundaries, constraints, census_raw, hazards, coastal_flood, distances = get_data()

    #Clip the data
    if not os.path.exists("data/clipped"):
        os.mkdir("data/clipped")

    clipped_census, clipped_hazards, clipped_coastal = clip_to_boundary(boundaries[0], census_raw, hazards, coastal_flood)

    clipped_census, clipped_hazards, clipped_coastal = open_clipped_data(hazards)
    logger.info('Clipping complete')

    #Process data
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
    for ind in pop:
        #Populate two of its attributes
        ind.densities = get_densities(ind, census)
        ind.valid = child_is_good(ind, max_density_possible, census)

    # Add the fitness values to the individuals by mappaing each individual with it fitness score
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        #As the fitness attribute is currently 'None' as this is a blank random child, then we pass it the fitness values
        ind.fitness.values = fit

    #Keep a running total of how many unique development plans have been created
    configurations_assessed = NO_parents

    #As we are to create 15 differnet pots of objective functions against another objetcive function, we shall have a list wih 15 lists to store the data points
    #             1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    pareto_set = [[], [], [], [], [], [], [], [], [], [], [] ,[] ,[], [] ,[]]

    #For each successful generation, add the parents to the pareto set so that they can be plotted out
    pareto_set = add_to_pareto_set(pareto_set, pop)

    #Create a blank MOPO list where each nested list represents the best case of each objective function (and total F-score) seen
    #           f_tsu  f_cflood  f_rflood f_liq,  f_dist  f_dev,  F-score
    MOPO_List = [[],      [],     [],      [],    [],      [],    []]

    #Update the MOPO list to see if we have any new superior solutions!
    MOPO_List = update_MOPO(MOPO_List, pop)

    if 0 in when_to_plot:
        #Then the user has specified that the intial parents spatial plans shall be plotted!
        fig_spatial, axs_spatial = plot_development_sites(parents=pop, gen_number=0, when_to_plot=when_to_plot, census=census, scheme=scheme)

    logger.info('Initial population created and entering GA loop now')

    parents = pop

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

                #The child, straight after birth, recieves a vaccination. This causes mutation which leads to autism and well...
                child = toolbox.mutate(parent)[0]

                #Sometimes the returned child is a list of the DEAP class so lets extract it if thats the case
                while type(child) != creator.Individual:
                    child = child[0]

            #Apply reproduction (random parent unchanged)
            else:
                #Select 1 parent via Roulette Selection to create a child. Basically, a random parent is a pedophile and acts to be a kid again.
                child = toolbox.select(individuals=parents, k=1)[0]

            #Update the child attributes with the correct ones if they are a new child (eg mut or crossover modules delete fitness values)
            if not child.fitness.valid:
                child.densities = get_densities(child, census)
                child.valid = child_is_good(child, max_density_possible, census)

                # Add the fitness values to the individuals
                child.fitness.values = toolbox.evaluate(child)

                #As this was a completely new child that has not been seen before, then we shall add it to the running total
                configurations_assessed += 1

            #Check to see if it is a bad child, and if it is bad then it is tossed into a volcano as a virgin sacrifice. The good child, however, is forced into an arranged marraige in its teens.
            if child.valid:
                children.append(child)


        #Now we have all the children all ready! lets mix them with the parents and select the fittest ones for the next generation!
        parents[:] = toolbox.select_best(parents + children)

        #For each successful generation, add the parents to the pareto set so that they can be plotted out
        pareto_set = add_to_pareto_set(pareto_set, parents)

        #Update the MOPO list to see if we have any new superior solutions!
        MOPO_List = update_MOPO(MOPO_List, parents)

        if gen_number in when_to_plot:
            #Then the user has specified that these parents spatial plans shall be plotted!
            fig_spatial, axs_spatial = plot_development_sites(parents, gen_number, when_to_plot, census, scheme, fig_spatial, axs_spatial)


        logger.info('Generation {} complete'.format(gen_number))

    logger.info('Genetic algorithm complete')




    ########### PHASE 3 - PARETO FRONTS AND OTHER PLOTS

    logger.info('Started plotting pareto results from the genetic algorithm')

    #check to see if a directory for pareto plots already exists, and create it if not
    if not os.path.exists("fig/{}".format(scheme)):
        os.mkdir("fig/{}".format(scheme))

    #Plot the pareto plots so we do our discussion and view the results
    plot_pareto_plots(pareto_set, scheme, NO_parents, NO_generations)

    #Plot the parents (for the generation selected by the user) and show their averge spatial plan! hahaha you got pranked bro. they got saved automatically in the last generation of the GA loop!

    logger.info('Now plotting ranked optimal-pareto results from the genetic algorithm')

    #Take the pareto set of the final parents and plot a spatial plan of ranked developement sites
    plot_ranked_pareto_sites(pareto_set, census, scheme, NO_parents, NO_generations)

    logger.info('Now plotting MOPO results from the genetic algorithm')

    #Now we want to showcase how each of the superior plans (from the MOPO list) actually have tradeoffs!
    plot_MOPO_plots(MOPO_List, census, scheme, NO_parents, NO_generations)

    #We wish to consider the best plan seen overall, and we want to 3D map the density changes!
    save_best_F_score_plan(MOPO_List, census, NO_parents, NO_generations)


    ######### PHASE 4 - ENDING

    logger.info("Kachow, all plots are done! thanks for running our code :)")

    #Print summary information of parameters used
    print(" ")
    logger.info("-----Summary of the parameters that were used in the algorithm:-----")
    print("Number of parents: {}".format(NO_parents))
    print("Number of generations: {}".format(NO_generations))
    print("User defined weightings of each objective function: {}".format(weightings))
    print("User defined weighting scheme: {}".format(scheme))
    print("Amount of dwellings needed: {} dwellings".format(required_dwellings))
    print("Recommended sustainable density used: {} dwellings/hectare".format(density_total))
    print("Maximum sustainable density used: {} dwellings/hectare".format(max_density_possible))

    print("Probability of applying a crossover to two D's: {}%".format(prob_crossover*100))
    print("Probability of mutating a D: {}%".format(prob_mutation*100))
    print("Probability of mutating an element (d) wihtin a D: {}%".format(prob_mutation*100))

    print("Total spatial plans/configuraitons assessed: {}".format(configurations_assessed))

    MOPO_sol_found = 0
    for obj_funct_MOPO in MOPO_List:
        MOPO_sol_found += len(obj_funct_MOPO)

    print("Total MOPO solutions found: {}".format(MOPO_sol_found))
    logger.info("---------- End of summary ----------")



if __name__ == "__main__":
    main()
