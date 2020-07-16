#-*- coding: utf-8 -*-
"""
NonDom_Sort Module 26/05/15
Author: Daniel Caparros-Midoowd

The non-dominated sorting module shown below takes the solutions found by the
optimisation module and determines those which are non-dominated. The algorithm
is based on Mishra & Harit's (2010) algorithm. Moreover the module can determine
non-dominated sets between specified objectives using the ‘ObjFun' variable.

Non dominated sorting algorithm to extract Pareto-optimal solutions.
The algorithm is based on Mishra & Harit's (2010) algorithm, first sort the solutions
by the first objective before iteratively comparing thier performances. By sorting them
we put solutions which are most likely to dominate at the start leading to less computations.
Throughout a non-dominated list of solutions is maintained and returned.

Requirements:
+ Objecives,f, requiring maximisation need to be multiplied by -1 prior
+ Solutions need to be in form [Solution number, Spatial Plan, Fitnesses]
+ Fitnesses need to be in the form [f1,f2,f3...]
+ Obj_Func need to be a list of fitness indexes
"""
SolNo, D, Obj_Col = 0,1,2 #specifies that obj funcs are stored in 3rd column

from copy import copy

def Sort(Solutions, ObjFunc):
    # ObjFunc is the set of objectives from which to conduct the non-Dominated
    # sorting, for example ObjFunc = [f1,f3] or ObjFunc = [f2,f3]
    
    NonDom_list = [] # list of non-dominated solutions
    Solution_list = copy(Solutions)

    # Sort the solution list by the first objective considered
    Solution_list.sort(key=lambda x: x[Obj_Col][ObjFunc[0]], reverse = False)

    # Pop the first ranked solution for that objective into the non dom list
    NonDom_list.append(Solution_list[0])
    Solution_list.pop(0)

    # Iteratively investigate solutions in the solution list against the non dom list
    for Sol in Solution_list: #Check each solution in the solution list

        row_count = -1 #keep a track of which row of the non_dom_list incase it needs to be popped

        # Iteratively compare the solution to solutions in the non dom list
        for NonDom_Sol in NonDom_list:
            row_count += 1
            # Assess the fitness of the
            Dominated, Dominates= Domination_Check(Sol[Obj_Col],NonDom_Sol[Obj_Col],ObjFunc)

            if Dominated == True:
                # If solution is found to be dominated we stop considering to save
                # computational time
                break

            elif Dominates == True:
                # if the solution in the nondom list is found to be dominated we pop it"
                NonDom_list.pop(row_count)
                break
        if Dominated == False:
            # If the solution is found to be undominated by all the solution in non dom list
            # it is added to it
            NonDom_list.append(Sol)

    # return the list of non dominated solutions

    return NonDom_list

def Domination_Check(Solution, NonDom_Solution,ObjFunc):
    # Assume both solutions are dominated untils there one instance where they outperform the other solution.
    Dominates = True # Stores if the solution dominates any solutions in the non dom list
    Dominated = True # Stores if the solution is dominated by a solution in the non dom list

    for Objective in (ObjFunc):
        # For each objective function under consideration
        if Solution[Objective] < NonDom_Solution[Objective]:
            # if the solution is found to outpeform (be less than) in any of the objectives
            # it is non dominated
            Dominated = False
        elif Solution[Objective] > NonDom_Solution[Objective]:
            # if the non dom solution is found to outpeform (be less than) in any
            # of the objectives it remains in the non-dom list
            Dominates = False

    # returns whether sol or nondom_sol is dominated
    return Dominated, Dominates
