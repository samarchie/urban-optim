"""
7th of September 2020
Author: Sam Archie and Jamie Fleming

The non-dominated sorting module shown below takes the solutions found by the
optimisation module and determines those which are non-dominated. The algorithm
is based on Capparos-Midwood's (2016) algorithm. Moreover the module can determine
non-dominated sets between specified objectives using the ‘ObjFun' variable.

Non dominated sorting algorithm to extract Pareto-optimal solutions.
The algorithm is based on Capparos-Midwood's (2016) algorithm, first sort the solutions
by the first objective before iteratively comparing thier performances. By sorting them
we put solutions which are most likely to dominate at the start leading to less computations.
Throughout a non-dominated list of solutions is maintained and returned.

Requirements:
+

"""

#Import necessary packages
import geopandas as gpd
import numpy as np
from genetic_algorithm import *
import random
from copy import copy


def Sort(F_scores):
    """

    """
    solutions = copy(F_scores)
    solutions.sort(key=lambda x: x[3][6])

    NonDom_list = [] # list of non-dominated solutions

    # Pop the first ranked solution for that objective into the non dom list
    NonDom_list.append(solutions[0])
    solutions.pop(0)

#    Solution = solutions[1]
#    Solution[1]
#    NonDom_list[0][1]

#    Domination_Check(Solution, NonDom_list[0])

    # Iteratively investigate solutions in the solution list against the non dom list
    for Solution in solutions: #Check each solution in the solution list

        row_count = 0 #keep a track of which row of the non_dom_list incase it needs to be popped

        # Iteratively compare the solution to solutions in the non dom list
        for NonDom_Sol in NonDom_list:
            # Assess the fitness of the
            Dominated, Dominates= Domination_Check(Solution, NonDom_Sol)

            if Dominated == True:
                # If solution is found to be dominated we stop considering to save computational time
                break

            elif Dominates == True:
                # if the solution in the nondom list is found to be dominated we pop it"
                NonDom_list.pop(row_count)
                break

            row_count += 1
        if Dominated == False:
            # If the solution is found to be undominated by all the solution in non dom list it is added to it
            NonDom_list.append(Solution)

    # return the list of non dominated solutions

    return NonDom_list


def Domination_Check(Solution, NonDom_Solution):
    # Assume both solutions are dominated untils there one instance where they outperform the other solution.
    Dominates = True # Stores if the solution dominates any solutions in the non dom list
    Dominated = True # Stores if the solution is dominated by a solution in the non dom list

    for Objective in range(0, 7):
        # For each objective function under consideration
        if Solution[3][Objective] < NonDom_Solution[3][Objective]:
            # if the solution is found to outpeform (be less than) in any of the objectives it is non dominated
            Dominated = False
        elif Solution[3][Objective] > NonDom_Solution[3][Objective]:
            # if the non dom solution is found to outpeform (be less than) in any of the objectives it remains in the non-dom list
            Dominates = False

    # returns whether sol or nondom_sol is dominated
    return Dominated, Dominates


def MOPO_update(MOPO_List, parents_gplus1):
    """
    checks the new set of parents (g+1) against the MOPO set, and updates the MOPO set if the new development plan has a better result in any of the objective functions
    parents_gplus1 is a list of tuples, containing an identifying index and a list F_scores for each D
    """

    # Sort the parents by each objective function. Check if the best parent for each
    # objective beats the current one in the MOPO set and if so update the MOPO with the better one
    parents_gplus1.sort(key=lambda x: x[1][0])
    if parents_gplus1[0][1][0] < MOPO_List[0][0]:
        MOPO_List[0][0] = parents_gplus1[0][1][0]
        MOPO_List[0][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_tsu")

    parents_gplus1.sort(key=lambda x: x[1][1])
    if parents_gplus1[0][1][1] < MOPO_List[1][0]:
        MOPO_List[1][0] = parents_gplus1[0][1][1]
        MOPO_List[1][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_cflood")

    parents_gplus1.sort(key=lambda x: x[1][2])
    if parents_gplus1[0][1][2] < MOPO_List[2][0]:
        MOPO_List[2][0] = parents_gplus1[0][1][2]
        MOPO_List[2][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_rflood")

    parents_gplus1.sort(key=lambda x: x[1][3])
    if parents_gplus1[0][1][3] < MOPO_List[3][0]:
        MOPO_List[3][0] = parents_gplus1[0][1][3]
        MOPO_List[3][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_liq")

    parents_gplus1.sort(key=lambda x: x[1][4])
    if parents_gplus1[0][1][4] < MOPO_List[4][0]:
        MOPO_List[4][0] = parents_gplus1[0][1][4]
        MOPO_List[4][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_dist")

    parents_gplus1.sort(key=lambda x: x[1][5])
    if parents_gplus1[0][1][5] < MOPO_List[5][0]:
        MOPO_List[5][0] = parents_gplus1[0][1][5]
        MOPO_List[5][1] = parents_gplus1[0][0]
        print("MOPO List Updated for f_dev")

    parents_gplus1.sort(key=lambda x: x[1][6])
    if parents_gplus1[0][1][6] < MOPO_List[6][0]:
        MOPO_List[6][0] = parents_gplus1[0][1][6]
        MOPO_List[6][1] = parents_gplus1[0][0]
        print("MOPO List Updated for F_scores")

    return MOPO_List
