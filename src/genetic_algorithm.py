# -*- coding: utf-8 -*-
"""
31st of August 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 2 of the project, specifically regarding the genetic algorthm.

"""

import deap
import geopandas as gpd
import os
import random
import numpy as np

# #Define genetic algorithm Parameters
# acceptable_dwelling_densities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] #Define what are acceptable densities for new areas (in dwelling/hecatres)
# NO_parents = 5 #number of parents/development plans in each iteration to make
# generations = 5 #how many generations/iterations to complete
# prob_crossover = 0.7 #probability of having 2 development plans cross over
# prob_mutation = 0.2 #probability of a development plan mutating
# weightings = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6] #weightings of each objective function
# required_dwellings = 20000 #amount of required dwellings over entire region
#
# census = gpd.read_file("data/processed/census_final.shp")

def create_initial_development_plans(NO_parents, required_dwellings, acceptable_dwelling_densities, census):
    """This module created the inital set of parents, which are lists of randomised development at randomised statistical areas.

    Parameters
    ----------
    NO_parents : Integer
        Number of parent (inital) develeopment plans to be created.
        required_dwellings : Integer
        The forecasted amount of dwellings to be constructed in the city district.
    acceptable_dwelling_densities : List
        A list fof integers which represent acceptable and sustainable densities in terms of dwelllings per hectare.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.

    Returns
    -------
    develepment_plans : List
        A list of NO_parents amount of lists. Each nested list contains floating point numbers which indicate the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame.
    addition_of_dwellings : List
        A list of NO_parents amount of lists. Each nested list contains integre numbers which indicate the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame.

    """

    develepment_plans = []
    addition_of_dwellings = []

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

            #Pick a random density to develop on the property
            density_total = random.choice(acceptable_dwelling_densities)
            #Find the density that needs to be added to get to this total
            density_add = max([0, density_total - existing_density - already_added_density])
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
        develepment_plans.append(development_plan_of_densities)
        addition_of_dwellings.append(assoc_addition_of_dwellings)


    return develepment_plans, addition_of_dwellings


#Each instance of D is evaluated against the performance functions (f_heat, f_flood etc.) and get a value F which is the sum of the performance functions, f.
