# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call upon any other functions it needs to do the genetic algorthm!

Good luck
"""

#Import all necessary modules from external sources
import os, warnings, random, sys, operator, array, math
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from deap import tools, base, creator

#This all us to run the code from the urban-optim directory (for ease of opening and saving data) whilst looking for further code/modules in the src folder by adding the filepath to the system path
sys.path.insert(0, str(sys.path[0]) + '/src/Christchurch')

#Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.
warnings.simplefilter("ignore")

#Import our home-made modules
from initialisation import *
from genetic_algorithm import *
from plotty_bois import *
from logger_config import *

#Set up the logging software so we can track efficieny of the genetic algortihm and see where code breaks
logger = logging.getLogger(__name__)




def main():
    """Now this is where the magic happens!"""
    ####### PHASE 1 - INTIALISATION #######

    #Get the algorithm parameters that can be changed by the user
    NO_parents, NO_generations, prob_crossover, prob_mutation, prob_mut_indiv, weightings, required_dwellings, scheme, density_total, min_density_possible, max_density_possible, when_to_plot = get_parameters()

    logger.info('Parameters for the algortihm are defined')

    #Get geospatial data (shapefiles) from the user
    boundaries, constraints, census_raw, hazards, coastal_flood, distances = get_data()
    logger.info('Data files for the algortihm are defined')

    #Clip the data files to the extend of the boundary, if it has not alreadyy taken place before
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

    else:
        census = gpd.read_file("data/processed/census_final.shp")

    logger.info('Processing/initialisation complete')

    # Plot the processed census data and check the objective functions are working as expected!
    plot_intialised_data(census, scheme, weightings)

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
        ind.valid = child_is_good(ind, min_density_possible, max_density_possible, census)

    # Add the fitness values to the individuals by mappaing each individual with it fitness score
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        #We pass it the fitness values to populate the attributes field!
        ind.fitness.values = fit

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


    ####### PHASE 2 - ITERATION PROCEDURE #######
    for gen_number in range(1, NO_generations + 1):
        i=0
        #In each generation, we need to create NO_parents amount of children! hence, create one at a time.
        children = []
        while len(children) < NO_parents:
            #Generate a random number between 0 and 1, and use this to test HoW we will create a new child! This is all based on the mu-plus-lambda evolution strategy
            op_choice = random.random()

            #Apply cross-over to two parents
            if op_choice < prob_crossover:
                #Select two parents via Roulette Selection to create a child
                parent1, parent2 = list(map(toolbox.clone, toolbox.select(individuals=parents, k=2)))
                #Perform a love-making ritual that binds the two parents till death do them part <3
                child = toolbox.mate(parent1, parent2)[0]
                logger.info('cross-over done')

            #Apply mutation to one parent
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
                logger.info('mutation done')

            #Apply cloning/reproduction (random parent unchanged)
            else:
                #Select 1 parent via Roulette Selection to create a child. Basically, a random parent is a pedophile and acts to be a kid again.
                child = toolbox.select(individuals=parents, k=1)[0]
                logger.info('cloning done')

            #Update the child attributes with the correct ones if they are a new child (eg mut or crossover modules delete fitness values)
            if not child.fitness.valid:
                child.densities = get_densities(child, census)
                logger.info('updated densities')
                child.valid = child_is_good(child, min_density_possible, max_density_possible, census)
                logger.info('checked validity')

                # Add the fitness values to the individuals
                child.fitness.values = toolbox.evaluate(child)
                logger.info('added fitnesses')

            #Check to see if it is a bad child, and if it is bad then it is tossed into a volcano as a virgin sacrifice. The good child, however, is forced into an arranged marraige in its teens.
            if child.valid:
                children.append(child)
                logger.info('child kept')
            else:
                logger.info('child killed')
            i += 1
            if i > 1000:
                break


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



    ####### PHASE 3 - PLOTTING AND OUTPUTS #######

    logger.info('Started plotting pareto results from the genetic algorithm')


    #Plot the pareto plots so we do our discussion and view the results
    plot_pareto_plots(pareto_set, scheme, NO_parents, NO_generations)

    #Plot the parents (for the generation selected by the user) and show their averge spatial plan! hahaha you got pranked bro. they got saved automatically in the last generation of the GA loop!

    logger.info('Now plotting ranked optimal-pareto results from the genetic algorithm')

    #Take the pareto set of the final parents and plot a spatial plan of ranked developement sites
    plot_ranked_pareto_sites(pareto_set, census, MOPO_List, scheme, NO_parents, NO_generations)

    logger.info('Now plotting MOPO results from the genetic algorithm')

    #Now we want to showcase how each of the superior plans (from the MOPO list) actually have tradeoffs!
    plot_MOPO_plots(MOPO_List, census, scheme, NO_parents, NO_generations)

    #We wish to consider the best plan seen overall, and we want to 3D map the density changes!
    logger.info('Now plotting best F_score results from the genetic algorithm')

    save_ranked_F_score_sites(parents, census, scheme, NO_parents, NO_generations)


    ####### PHASE 4 - ENDING #######

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
    print("Minimum sustainable density used: {} dwellings/hectare".format(min_density_possible))
    print("Maximum sustainable density used: {} dwellings/hectare".format(max_density_possible))

    print("Probability of applying a crossover to two D's: {}%".format(prob_crossover*100))
    print("Probability of mutating a D: {}%".format(prob_mutation*100))
    print("Probability of mutating an element (d) within a D: {}%".format(0.05*100))

    MOPO_sol_found = 0
    for obj_funct_MOPO in MOPO_List:
        MOPO_sol_found += len(obj_funct_MOPO)
    print("Total MOPO solutions found: {} plans".format(MOPO_sol_found))

    #Set a blank list and add individuals to it that are on the front
    pareto_parents = []
    for objective_pair in pareto_set:
        pareto_front = identify_pareto_front(objective_pair)

        for point in pareto_front:
            #Check to make sure there isnt double ups of parents in the set. As one parent could be optimal
            if point[-1] not in pareto_parents:
                pareto_parents.append(point[-1])

    print("Amount of spatial plans on the pareto-front that are optimal in at least one objective: {} plans".format(len(pareto_parents)))

    logger.info("---------- End of summary ----------")



if __name__ == "__main__":
    main()
