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
from src.genetic_algorithm import *
import random

census = gpd.read_file("data/processed/census_final.shp")
census

max(census['F_score'])

objective_functions = ['f_tsu', 'f_cflood', 'f_rflood', 'f_liq', 'f_dist', 'f_dev', 'F_score']
#index        f_tsu            f_cflood            f_rflood             f_liq               f_dist              f_dev              F_score
#[(1, [73.41722296047094, 239.63333333333455, 816.50000000000130, 2324.0900000000000, 461.04649317735254, 137.65539336823363, 4052.3424428393932]),
# (2, [68.44216867312252, 198.30000000000052, 666.33333333333460, 2072.6633333333330, 467.27333198655670, 483.07554824970396, 3956.0877155760510]),
# (3, [93.78114078568109, 251.85000000000073, 617.33333333333440, 1709.9199999999996, 462.51575055248367, 345.07654005011780, 3480.4767647216170]),
# (4, [66.77915599208782, 271.71666666666670, 1035.6666666666688, 1754.4533333333330, 486.19605761755247, 628.28276762863160, 4243.0946479049410]),
# (5, [43.72476358181851, 108.40000000000016, 749.33333333333460, 1572.7799999999975, 458.87802733956440, 989.39999754461630, 3922.5161217993320])]

F_scores = [(1, [73.41722296047094, 239.63333333333455, 816.5000000000013, 2324.09, 461.04649317735254, 137.65539336823363, 4052.3424428393932]), (2, [68.44216867312252, 198.30000000000052, 666.3333333333346, 2072.663333333333, 467.2733319865567, 483.07554824970396, 3956.087715576051]), (3, [93.78114078568109, 251.85000000000073, 617.3333333333344, 1709.9199999999996, 462.51575055248367, 345.0765400501178, 3480.476764721617]), (4, [66.77915599208782, 271.7166666666667, 1035.6666666666688, 1754.453333333333, 486.19605761755247, 628.2827676286316, 4243.094647904941]), (5, [43.72476358181851, 108.40000000000016, 749.3333333333346, 1572.7799999999975, 458.8780273395644, 989.3999975446163, 3922.516121799332])]
F_scores


def sort(F_scores, ):
    """

    """
    solutions = copy(F_scores)
    solutions.sort(key=lambda x: x[1][6])

    Solution = solutions[0]

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
                # If solution is found to be dominated we stop considering to save
                # computational time
                break

            elif Dominates == True:
                # if the solution in the nondom list is found to be dominated we pop it"
                NonDom_list.pop(row_count)
                break

            row_count += 1
        if Dominated == False:
            # If the solution is found to be undominated by all the solution in non dom list
            # it is added to it
            NonDom_list.append(Solution)

    # return the list of non dominated solutions

    return NonDom_list

def Domination_Check(Solution, NonDom_Solution):
    # Assume both solutions are dominated untils there one instance where they outperform the other solution.
    Dominates = True # Stores if the solution dominates any solutions in the non dom list
    Dominated = True # Stores if the solution is dominated by a solution in the non dom list

    for Objective in range(0, 7):
        # For each objective function under consideration
        if Solution[1][Objective] < NonDom_Solution[1][Objective]:
            # if the solution is found to outpeform (be less than) in any of the objectives it is non dominated
            Dominated = False
        elif Solution[1][Objective] > NonDom_Solution[1][Objective]:
            # if the non dom solution is found to outpeform (be less than) in any of the objectives it remains in the non-dom list
            Dominates = False

    # returns whether sol or nondom_sol is dominated
    return Dominated, Dominates


def MOPO_update(MOPO_List, parents_gplus1):
    """
    checks the new set of parents (g+1) against the MOPO set, and updates the MOPO set if the new development plan has a better result in any of the objective functions
    parents_gplus1 is a list of tuples, containing an identifying index and a list F_scores for each D
    """

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
