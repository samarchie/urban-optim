# -*- coding: utf-8 -*-
"""
31st of August 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 2 of the project, specifically regarding the genetic algorthm.

"""

from deap import tools
import os
import random
import numpy as np

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
        The number of individiuals to select.

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


def apply_crossover(selected_parents):
    """This module crossovers the 2 selected parents using a 2-point crossover procedure.

    Parameters
    ----------
    selected_parents : List
        A list of 2 lists which is a development plan, which were selected via Roulette tournament. The nested lists contains an index value (representing which development plan number it is) and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. The third nested list contains floating point numbers which is the scores against each of the 6 objective functions, and then the summation which acts as the overall development plan F-score!

    Returns
    -------
    children_created : Tuple
        A tuple of 2 lists. Each list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well for the new (child) development plan.

    """
    #Get the dwelling addition lists which is what we will crossover.
    buildings_one = selected_parents[0][2][:]
    buildings_two = selected_parents[1][2][:]

    #Do the cross-over procedure - which is all taken care of thanks to DEAP <3
    children_created = tools.cxTwoPoint(buildings_one, buildings_two)


    return children_created


def apply_mutation(selected_parent):
    """This module mutates a selected parent and thus creates a child via shuflfing the amount of buildings to add in each statiscal area.

    Parameters
    ----------
    selected_parent : List
        A list of 1 lists which is a development plan, which was selected via Roulette tournament. The nested list contains an index value (representing which development plan number it is) and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. The third nested list contains floating point numbers which is the scores against each of the 6 objective functions, and then the summation which acts as the overall development plan F-score!

    Returns
    -------
    children_created : List
        A list of 1 list, as there is only one child created. The nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well for the new (child) development plan.

    """

    prob_mut_indiv = 0.05 #probability of mutating an element d_i within D_i

    #Extract the buildings addition list of the selected parents
    buildings = selected_parent[0][2][:]
    #Do the mutation procedure - which is all taken care of thanks to DEAP <3
    child_created = tools.mutShuffleIndexes(buildings, prob_mut_indiv)

    return [child_created]


def update_densities(children_created, census):
    """This module takes the children (additions of dwellings) and calculates the associated density of development.

    Parameters
    ----------
    children_created : Tuple
        A tuple of 2 lists. Each list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well for the new (child) development plan.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    children_plans
        A list of NO_parent amounts of lists. Each list contains two nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well.

    """

    #Calculate the polygon areas of each statistical area from the GeoDataFrame
    areas = census.area

    children_plans = []
    #Update each child seperately
    for child_number in range(len(children_created)):
        child = children_created[child_number]

        #Find out how many statistical areas there are to begin with, and create a blank list
        no_of_areas = len(child)
        total_densities = [0] * no_of_areas

        #Update each statistical area's density by using the index number (as every lists is in the same order as the GeoDataFrame Census)
        for prop_index in range(no_of_areas):
            prop_area = areas[prop_index]
            new_dwellings = child[prop_index]

            #Calculate the added density (from new dwellings) and add it to the already existing density
            total_densities[prop_index] = (new_dwellings / prop_area) + census.loc[prop_index, "Density"]

        #Append all the information into one list (in the correct order) and add to the master list of children/new development plans
        children_plans.append([total_densities, child])

    return children_plans


def verify_densities(children_plans, density_total, census):


    #Calculate the polygon areas of each statistical area from the GeoDataFrame
    areas = census.area

    #Check each child one at a time
    for child in children_plans:

        #Extract the projected densities of each statistical area for the child plan
        densities_list = child[1][:]

        #Check each statistical area to make sure it is under the threshold amount
        for prop_index in range(len(densities_list)):

            if densities_list[prop_index] > density_total:
                #Then unfortunately the addedd dwellings causes the density to exceed the sustainable urban development limit set by the user
                wrong_density = densities_list[prop_index]

                #Calculate the amount of houses over the limit
                extra_dwellings = (wrong_density - density_total) * areas[prop_index]
                #Change the density to be the maximum
                child[1][prop_index] = density_total

                #Assign the extra houses to a different statistical area so that we reach the same amount of houses overall




    return children
