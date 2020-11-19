# -*- coding: utf-8 -*-
"""
31st of August 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 2 of the project, specifically regarding the genetic algorthm.

"""

from deap import tools, base, creator
import numpy as np
import os, random, array


def initialise_deap(required_dwellings, density_total, census, NO_parents, prob_mut_indiv, max_density_possible):
    """This module creates the toolbox that is used for the Genetic Algorithm, and provides links to caller functions oh how to create, modify and evaluate development plans.

    Parameters
    ----------
    required_dwellings : Integer
        Number of projected dwellings required to house future residents in the urban area.
    density_total : List of Floating Point Number
        The acceptable densities for new areas (in dwelling/hecatres) for sustainable urabn development.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    prob_mut_indiv : Floating Point Number
        A number between 0 and 1 that represents the probability of mutating an element (d) wihtin an individual (D).

    Returns
    -------
    toolbox : deap.base.ToolBox Class
        A toolbox for evolution that contains the evolutionary operators, and how to apply them.

    """

    #Set up the DEAP class called an individual, and apply the weights to the Fitness class as well
    creator.create("FitnessMulti", base.Fitness, weights=(-1,)*6)

    #Set up the individual, with attributes for fitnesses, densities and if it is a good child or not.
    creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMulti, densities=None, valid=None)

    #Create the toolbox where all the population is saved
    toolbox = base.Toolbox()

    #Initialise how to create an individual via the create_initial_development_plan module, and also detail how to make a population (repeat making individuals till there are NO_parents)
    #Basically, an individual will be a list of len(census) long that has intergers that indicate how many buildings are to be built in that statiscal area.
    toolbox.register("individual", create_initial_development_plan, creator.Individual, required_dwellings=required_dwellings, density_total=density_total, census=census)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    #Now we need the register the genetic algorithm methods that we will use!
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=prob_mut_indiv)
    toolbox.register("select_best", tools.selNSGA2, k=NO_parents, nd='standard')
    toolbox.register("select", tools.selRoulette)

    #We also need to specifiy some home-made functions that we'd like to use as well
    toolbox.register("evaluate", evaluate_development_plan, census=census)

    return toolbox


def create_initial_development_plan(ind_class, required_dwellings, density_total, census):
    """This module created the inital set of parents, which are lists of randomised development at randomised statistical areas.

    Parameters
    ----------
    NO_parents : Integer
        Number of parent (inital) develeopment plans to be created.
    required_dwellings : Integer
        The forecasted amount of dwellings to be constructed in the city district.
    density_total : List of Floating Point Number
        The acceptable densities for new areas (in dwelling/hecatres) for sustainable urabn development.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    ind : deap.class.Individual Class
         The list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. However, it is no ordinary list - it is a DEAP Individual, so it looks like a list when you print it out (or iterate through) but in fact it also has attributes such as fitness, validity and densities. These attributes are blank still.

    """

    #Create rolling lists that we will use, so we should make them empty first
    development_plan_of_densities = [0] * len(census)
    assoc_addition_of_dwellings = [0] * len(census)

    #Use a while loop to keep on adding dwellings (densifying) until the required amount is met!
    dwellings_added = 0
    while dwellings_added < required_dwellings:
        #Pick a random statistical area to develop on
        prop_index = random.randint(0, len(census) - 1)
        property_data = census.loc[census["index"] == prop_index]

        #and get its attributes (density already present and the area)
        existing_density = property_data["Density"].values[0]
        area_of_property = property_data.area.values[0] / 10000 #in hectares
        already_added_density = development_plan_of_densities[prop_index] #added from this module

        #Pick a sustainable density at random to assign to this statistical area
        density_random = random.choice(density_total)

        #there might be a case where the existing density of a statistical area is greater than one of the chosen sustainable densities. hence, we need to make sure in the next line we dont add a negative number!
        density_to_add = max(0, density_random - existing_density - already_added_density)
        #and convert to dwellings (round down to nearest integer as you cant have half houses hahahaha)
        dwellings_to_add = np.floor(density_to_add * area_of_property)
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

    ind = ind_class(assoc_addition_of_dwellings)

    return ind


def get_densities(ind, census):
    """This module takes the children (additions of dwellings) and calculates the associated density of development.

    Parameters
    ----------
    ind : deap.base.Individual Class
         The list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. However, it is no ordinary list - it is a DEAP Individual, so it looks like a list when you print it out (or iterate through) but in fact it also has attributes such as fitness, validity and densities. These attributes are blank still.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    densities : array.array
        An array represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. T

    """
    #Get the areas of the statistical areas
    areas = census.area / 10000 # in hectares

    #Find out how many statistical areas there are to begin with, and create a blank list
    densities = [0] * len(areas)

    #Update each statistical area's density by using the index number (as every lists is in the same order as the GeoDataFrame Census)
    for prop_index in range(0, len(areas)):

        prop_area = areas[prop_index] #area of statistical area
        new_dwellings = ind[prop_index] #dwellings to add, taken from the Individual

        #Calculate the added density (from new dwellings)
        densities[prop_index] = (new_dwellings / prop_area)

    #Return the densities as an array for code efficieny (arrays are shown to be quicker as part of the genetic algorithm compared to lists!)
    densities = array.array("d", densities)

    return densities


def child_is_good(child, min_density_possible, max_density_possible, census):
    """This module evaluate whether a child satisfies the constraint of a specified density limit.

    Parameters
    ----------
    child : deap.base.Individual Class
         The list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. However, it is no ordinary list - it is a DEAP Individual, so it looks like a list when you print it out (or iterate through) but in fact it also has attributes such as fitness, validity and densities. Only the densities attribute has been filled in.
    max_density_possible : Floating Point Number
        Maximum sustainable density in dwellings per hectare.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    is_good_child : Bool
        Returns True if the all statiscal areas have a density less than the threshold. Otherwise, it returns False.

    """
    #The child is assumed to be good until it is shown to be bad!
    is_good_child = True

    #Check each statistical area to make sure it is within the defined sustainable density thresholds
    for prop_index in range(len(child.densities)):
        #Extract the current density from the GeoDataFrame
        existing_density = float(census.loc[prop_index, "Density"])
        density_to_add = float(child.densities[prop_index])

        if density_to_add > 0: # Check validity of changed SAs. Unchanged SAs will most likely not meet sustainability thresholds
            if density_to_add + existing_density > max_density_possible:
                #Then unfortunately the added dwellings causes the density to exceed the upper sustainable urban development limit set by the user
                is_good_child = False
                break

            if density_to_add + existing_density < min_density_possible:
                #Then unfortunately the new total dwellings does not reach the lower sustainable urban development limit set by the user
                is_good_child = False
                break

    return is_good_child


def evaluate_development_plan(child, census):
    """This module evaluates and scores each individual development plan with f scores, that incorporates how many houses are developed in which bad statistical areas.

    Parameters
    ----------
    child : deap.base.Individual Class
         The list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well. However, it is no ordinary list - it is a DEAP Individual, so it looks like a list when you print it out (or iterate through) but in fact it also has attributes such as fitness, validity and densities. The densities and validities attribute has been filled in.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 columns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    f_scores : Tuple
        A tuple of 6 floating point numbers, which represents the scores against each of the 6 objective functions of the development plan ("child").

    """

    #State the column names of the objectiv functions
    obj_funcs = ['f_tsu', 'f_cflood', 'f_rflood', 'f_liq', 'f_dist', 'f_dev']

    f_scores_running_total = [0] * 6 #one sum for each objective function

    #Check each statistical area in the development plan,
    for prop_index in range(0, len(census)):
        #Find the amount of dwellings to built on each statistical area
        dwellings_added = child[prop_index]

        #If the site is to be developed, then assign a total F-score, weighted by how many dwellings are to be built and add to the rolling sum for the development plan
        if dwellings_added > 0:
            #Find the objective scores for each f-function and use the weightings! Add it to the rolling sums list!
            obj_counter = 0
            for obj_func in obj_funcs:

                #Extract the f score for the property
                f_prop_score = census.loc[prop_index, obj_func]
                #Use a weighting scheme that is proportional to the amount of dwellings that are to be built on that site
                f_scores_running_total[obj_counter] += f_prop_score * dwellings_added
                obj_counter += 1

    #Now make the list immutable by converting it to a tuple
    f_scores = tuple(f_scores_running_total)

    return f_scores


def update_MOPO(MOPO_List, parents):
    """This module checks the new set of parents against the MOPO set from the previous generation, and updates the MOPO set if any new development plan has a better result in any of the objective functions.

    Parameters
    ----------
    MOPO_List : List of Lists
        A list of 7 lists, where each nested list represents an objective functions, such as f_dist, and the sum of the 6 objective functions. In each of these nested lists is Individuals which have been evaliated to be the best seen for that objective at the present time.
    parents : List of deap.class.Individuals
         A list of NO_parents amount of DEAP individuals that represents Individuals at the end of a generation.

    Returns
    -------
    MOPO_List : List of Lists
        A list of6 lists, where each nested list represents an objective functions, such as f_dist. In each of these nested lists is Individuals which have been evaliated to be the best seen for that objective at the present time. It is not replaced when a better Individual is found, but rather the new and better one is appended to the back of the list.

    """

    #if the list is empty, then we need to add the initial parents to it
    if MOPO_List == [[], [], [], [], [], [], []]:

        for obj_num in range(0, 6):
            #Sort by the objective function that we are looking at, and then add the best Individual to the MOPO list in the right spot.
            parents.sort(key=lambda x: x.fitness.values[obj_num])
            #Add the best one to the MOPO list
            MOPO_List[obj_num].append(parents[0])

        #Sort by the sum of the objective functions ("F-score") and the best one is added to the MOPO list
        parents.sort(key=lambda x: sum(x.fitness.values))
        MOPO_List[6].append(parents[0])

    # Sort the parents by each objective function. Check if the best parent for each objective beats the current one in the MOPO set and if so update the MOPO with the better one.
    else:
        #1st objective function - f_tsunami
        parents.sort(key=lambda x: x.fitness.values[0])
        if parents[0].fitness.values[0] <= MOPO_List[0][-1].fitness.values[0]:
            MOPO_List[0].append(parents[0])

        #2nd objective function - f_coastal_flooding
        parents.sort(key=lambda x: x.fitness.values[1])
        if parents[0].fitness.values[1] <= MOPO_List[1][-1].fitness.values[1]:
            MOPO_List[1].append(parents[0])

        #3rd objective function - f_river_flooding
        parents.sort(key=lambda x: x.fitness.values[2])
        if parents[0].fitness.values[2] <= MOPO_List[2][-1].fitness.values[2]:
            MOPO_List[2].append(parents[0])

        #4th objective function - f_liquefaction_vulnerability
        parents.sort(key=lambda x: x.fitness.values[3])
        if parents[0].fitness.values[3] <= MOPO_List[3][-1].fitness.values[3]:
            MOPO_List[3].append(parents[0])

        #5th objective function - f_distance
        parents.sort(key=lambda x: x.fitness.values[4])
        if parents[0].fitness.values[4] <= MOPO_List[4][-1].fitness.values[4]:
            MOPO_List[4].append(parents[0])

        #6th objective function - f_district_planning
        parents.sort(key=lambda x: x.fitness.values[5])
        if parents[0].fitness.values[5] <= MOPO_List[5][-1].fitness.values[5]:
            MOPO_List[5].append(parents[0])

        #Overall objective function - F-score
        parents.sort(key=lambda x: sum(x.fitness.values))
        if sum(parents[0].fitness.values) <= sum(MOPO_List[6][-1].fitness.values):
            MOPO_List[6].append(parents[0])

    return MOPO_List
