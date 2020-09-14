# -*- coding: utf-8 -*-
"""
31st of August 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 2 of the project, specifically regarding the genetic algorthm.

"""

from deap import tools
import geopandas as gpd
import os
import random
import numpy as np
import matplotlib.pyplot as plt

# #Define genetic algorithm Parameters
# density_total = 10 #Define what are acceptable maximum densities for new areas (in dwelling/hecatres)
# NO_parents = 5 #number of parents/development plans in each iteration to make
# generations = 5 #how many generations/iterations to complete
# prob_crossover = 0.7 #probability of having 2 development plans cross over
# prob_mutation = 0.2 #probability of a development plan mutating
# weightings = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6] #weightings of each objective function
# required_dwellings = 20000 #amount of required dwellings over entire region
#
# census = gpd.read_file("data/processed/census_final.shp")


def create_initial_development_plans(NO_parents, required_dwellings, density_total, census):
    """This module created the inital set of parents, which are lists of randomised development at randomised statistical areas.

    Parameters
    ----------
    NO_parents : Integer
        Number of parent (inital) develeopment plans to be created.
    required_dwellings : Integer
        The forecasted amount of dwellings to be constructed in the city district.
    density_total : Floating Point Number
        The acceptable maximum densities for new areas (in dwelling/hecatres) for sustainable urabn development.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    development_plans : List
        A list of NO_parents amount of lists. Each list contains an index value (representing which development plan number it is) and two nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well.

    """

    development_plans = []

    #For each required development plan:
    for number in range(0, NO_parents):
        #Create a list, where each index is the row of the processed_column (eg statistical area) and each SA is densifiied by 0 dwellings/hecatres to start with
        development_plan_of_densities = [0] * len(census)
        assoc_addition_of_dwellings = [0] * len(census)

        #Use a while loop to keep on adding dwellings (densifying) untill the required amount is met!
        dwellings_added = 0
        while dwellings_added < required_dwellings:
            #Pick a random statistical area to develop on
            prop_index = random.randint(0, len(census) - 1)
            property_data = census.loc[census["index"] == prop_index]

            #and get its attributes (density already present and the area)
            existing_density = property_data["Density"].values[0]
            area_of_property = property_data.area.values[0] / 10000 #in hectares
            already_added_density = development_plan_of_densities[prop_index] #added from this module

            #Pick a density (under the sustainable threshold) that shall be used to densify this statistical area
            density_add = random.uniform(0, density_total - existing_density - already_added_density)
            #and convert to dwellings (round down to nearest integer as you cant have half houses hahahaha)
            dwellings_to_add = np.floor(density_add * area_of_property)
            #Update the density due to the rounding down of dwellings added
            density = dwellings_to_add / area_of_property

            #Check if not going over the required dwellings and add to totals and development_plans accordingly
            if dwellings_to_add + dwellings_added < required_dwellings:
                dwellings_added += dwellings_to_add
                development_plan_of_densities[prop_index] += density
                assoc_addition_of_dwellings[prop_index] += dwellings_to_add

            else:
                #The density that was randomised was too much! So reduce it
                dwellings_to_add = required_dwellings - dwellings_added
                dwellings_added = required_dwellings #to stop the while loop as we now have enough dwellings that were required

                #Calculate the new density
                new_density = dwellings_to_add / area_of_property # in dw/ha
                development_plan_of_densities[prop_index] += density
                assoc_addition_of_dwellings[prop_index] += dwellings_to_add

        #Once the required amount of dwellings to add is successful, the development plan is complete. Append a copy of the development plan to the master list and keep on iterating to get enough development plans
        development_plan = [number, development_plan_of_densities, assoc_addition_of_dwellings]
        development_plans.append(development_plan)

    return development_plans


def evaluate_development_plans(development_plans, census):
    """This module evaluates and scores each individual development plan with a F scores, that incorporates how many houses are developed in which bad statistical areas.

    Parameters
    ----------
    development_plans : List
        A list of NO_parents amount of lists. Each list contains an index value (representing which development plan number it is) and two nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 columns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    development_plans : List
        A list of NO_parents amount of lists. Each list contains an index value (representing which development plan number it is) and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. The third nested list contains floating point numbers which is the scores against each of the 6 objective functions, and then the summation which acts as the overall development plan F-score!

    """

    #Want to evaluate one development plan at a time
    for dev_index in range(0, len(development_plans)):
        #Get the development plan data
        development_plan = development_plans[dev_index]

        f_scores_running_total = [0] * 6 #one sum for each objective function

        #Check each statistical area in the development plan,
        for prop_index in range(0, len(census)):
            #Find the amount of houses to built on each statistical area
            houses_added = development_plan[2][prop_index]

            #If the site is to be developed, then assign a total F-score, weighted by how many houses are to be built and add to the rolling sum for the development plan
            if houses_added > 0:
                #Find the objective scores for each f-function and use the weightings! Add it to the rolling sums list!
                obj_funcs = ['f_tsu', 'f_cflood', 'f_rflood', 'f_liq', 'f_dist', 'f_dev']
                obj_counter = 0
                for obj_func in obj_funcs:
                    f_prop_score = census.loc[prop_index, obj_func]
                    f_scores_running_total[obj_counter] += f_prop_score * houses_added
                    obj_counter += 1

        #Calculate the summation of the individual objective functions, which will be the F-score.
        f_scores_running_total.append(sum(f_scores_running_total))

        #Update the original development_plans list with the new tuple of values.
        development_plans[dev_index].append(f_scores_running_total)

    return development_plans


def do_roulette_selection(development_plans, k):
    """This module selects k amount of individuals using a Roulette Selection procedure.

    Parameters
    ----------
    development_plans : List
        A list of NO_parents amount of lists. Each list contains an index value (representing which development plan number it is) and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. The third nested list contains floating point numbers which is the scores against each of the 6 objective functions, and then the summation which acts as the overall development plan F-score!
    k : Integer
        The number of individiuals to select

    Returns
    -------
    selected_parents : List
        A list of k amount of lists, which were selected via Roulette tournament. Each list contains an index value (representing which development plan number it is) and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. The third nested list contains floating point numbers which is the scores against each of the 6 objective functions, and then the summation which acts as the overall development plan F-score!

    """

    #In order to find the fitness of each dveleopment plan, it is simply the reciprocal of the F_score. Hence lower F_scores (which are superior) will be assigned a (relatively) higher fitness value
    fitness = [1 / development_plans[ind][3][6] for ind in range(len(development_plans))]
    sum_fitness = sum(fitness)

    #Zip the development plans and scores together to be able to sort by the F-score
    sorted_individuals = [[score, ind] for score, ind in sorted(zip(fitness, development_plans))]

    selected_parents = []
    for i in range(k):
        #Pick a random number to establish the breaking point, which chooses the individual
        threshold = random.random() * sum_fitness

        rolling_sum = 0
        for index in range(len(sorted_individuals)):
            individual = sorted_individuals[index]

            #Find and add the fitness value for that individual to the rolling sum
            rolling_sum += individual[0]
            if rolling_sum > threshold:
                #Then this is a chosen individual and we use it for crossover or whatever we need! Append the parent data to the master list
                selected_parents.append(individual[1])
                break

    return selected_parents


def apply_crossover(development_plan_index, development_plans):

    #Determine the development plan picked for cross-over
    development_plan = development_plans[development_plan_index]

    #Pick another plan to crossover the original with
    random_index = random.randrange(len(development_plans))
    other_development_plan = development_plans[random_index]

    #Make sure it isn't the same as the one that was meant to be changed lmao!
    while development_plan_index == random_index:
        random_index = random.randrange(no_of_plans)
        other_development_plan = development_plans[random_index]

    print("crossovered {} and {}".format(development_plan_index, random_index))

    #Get the dwelling addition lists which is what we will crossover.
    buildings_one = development_plan[2]
    building_two = other_development_plan[2]

    #Do the cross-over procedure - which is all taken care of thanks to DEAP <3
    new_development_plan, new_other_development_plan = tools.cxTwoPoint(buildings_one, building_two)

    #Update the total development plans list with the 2 new/modified/cross-overed development plans
    development_plans[development_plan_index][2] = new_development_plan
    development_plans[random_index][2] = new_other_development_plan

    return development_plans


def apply_mutation(development_plan):

    prob_mut_indiv = 0.05 #probability of mutating an element d_i within D_i

    #Do the mutation procedure - which is all taken care of thanks to DEAP <3
    development_plan = tools.mutUniformInt(development_plan, lower_bound,  upper_bound, prob_mut_indiv)

    return development_plan


def update_densities(development_plans, census):

    #Calculate the polygon areas of each statistical area from the GeoDataFrame


    #Update each development plan seperately
    for development_plan in development_plans:
        #Find out how many statistical areas there are to begin with, and create a blank list
        no_of_areas = len(development_plan[1])
        updated_densities = [0] * no_of_areas

        #Update each statistical area's density by using the index number (as every lists is in the same order as the GeoDataFrame Census)
        # for prop_index in range(0, no_of_areas):
        #     prop_area =

    return development_plans
