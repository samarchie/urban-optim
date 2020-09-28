"""
24th of September 2020
Author: Sam Archie and Jamie Fleming

beep boop here some pretty graphs

"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
#from paretochart.paretochart import pareto

def add_to_pareto_set(pareto_set, parents):
    """This module adds the parents from each generation to the pareto set. Takes all Development plans for this generation, and adds all parents to the pareto_set to be plotted later.
    Pareto set is essentially a list of all objective function combinations found in the GA

    Parameters
    ----------
    paretofront_set : List
        A list of 15 nested lists. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions.
    parents : List
        A list of NO_parent amounts of lists. Each list contains an index value and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well.The third nested list represents the scores of the parent against each objective function and the overall F-score.

    Returns
    -------
    paretofront_set : List
        A list of 15 nested lists, updated with parents from a generation. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions.

    """

    # Iterate through all current development plans
    for parent in parents:
        # Check if each unique objective pair has been added yet, and add it if not
        if (parent[2][0], parent[2][1]) not in pareto_set[0]:
            pareto_set[0].append((parent[2][0], parent[2][1]))
        if (parent[2][0], parent[2][2]) not in pareto_set[1]:
            pareto_set[1].append((parent[2][0], parent[2][2]))
        if (parent[2][0], parent[2][3]) not in pareto_set[2]:
            pareto_set[2].append((parent[2][0], parent[2][3]))
        if (parent[2][0], parent[2][4]) not in pareto_set[3]:
            pareto_set[3].append((parent[2][0], parent[2][4]))
        if (parent[2][0], parent[2][5]) not in pareto_set[4]:
            pareto_set[4].append((parent[2][0], parent[2][5]))

        if (parent[2][1], parent[2][2]) not in pareto_set[5]:
            pareto_set[5].append((parent[2][1], parent[2][2]))
        if (parent[2][1], parent[2][3]) not in pareto_set[6]:
            pareto_set[6].append((parent[2][1], parent[2][3]))
        if (parent[2][1], parent[2][4]) not in pareto_set[7]:
            pareto_set[7].append((parent[2][1], parent[2][4]))
        if (parent[2][1], parent[2][5]) not in pareto_set[8]:
            pareto_set[8].append((parent[2][1], parent[2][5]))

        if (parent[2][2], parent[2][3]) not in pareto_set[9]:
            pareto_set[9].append((parent[2][2], parent[2][3]))
        if (parent[2][2], parent[2][4]) not in pareto_set[10]:
            pareto_set[10].append((parent[2][2], parent[2][4]))
        if (parent[2][2], parent[2][5]) not in pareto_set[11]:
            pareto_set[11].append((parent[2][2], parent[2][5]))

        if (parent[2][3], parent[2][4]) not in pareto_set[12]:
            pareto_set[12].append((parent[2][3], parent[2][4]))
        if (parent[2][3], parent[2][5]) not in pareto_set[13]:
            pareto_set[13].append((parent[2][3], parent[2][5]))

        if (parent[2][4], parent[2][5]) not in pareto_set[14]:
            pareto_set[14].append((parent[2][4], parent[2][5]))

    return pareto_set


def plot_pareto_fronts(pareto_set):
    """
    pretty self explanatory tbh
    """

    # set up subplots
    rows = 5 # Number of rows of subplots
    cols = 3 # Number of columns of subplots
    fig, axs = plt.subplots(rows, cols, figsize=[20, 20])

    #set up subplot subtitles
    subtitles = ['f_tsu vs f_cflood', 'f_tsu vs f_rflood', 'f_tsu vs f_liq', 'f_tsu vs f_dist', 'f_tsu vs f_dev', 'f_cflood vs f_rflood', 'f_cflood vs f_liq', 'f_cflood vs f_dist', 'f_cflood vs f_dev', 'rflood vs f_liq', 'rflood vs f_dist', 'rflood vs f_dev', 'f_liq vs f_dist', 'f_liq vs f_dev', 'f_dist vs f_dev']

    # Set up plot indexes so we know where to plot each objective pair
    # these will iterate
    index = 0
    col = 0
    row = 0
    for objective_pair in pareto_set:
        # Create x and y coordinates for each objective pair
        xs1 = [x[0] for x in objective_pair]
        ys1 = [y[1] for y in objective_pair]

        #Find which points are on objective front, and assign their x and y coordinates in a plotable format
        pareto_front = identify_pareto_front(objective_pair)
        pareto_front.sort()

        xs2 = [x[0] for x in pareto_front]
        ys2 = [y[1] for y in pareto_front]

        # Yay let make pretty picture
        axs[row, col].scatter(xs1, ys1, marker='x')
        axs[row, col].plot(xs2, ys2)
        axs[row, col].set_title(subtitles[index])

        #Logic to keep track of which plot we are up to
        if col < cols-1:
            col += 1
        else:
            col = 0
            row += 1

        index += 1



    if not os.path.exists("fig/final"):
        os.mkdir("fig/final")

        # Save figure
    plt.savefig("fig/final/pareto_fronts.png", transparent=False, dpi=600)

    # Show the plots
    plt.show()


def identify_pareto_front(scores):
    """

    """
    # Count number of items
    scores = np.asarray(scores)
    population_size = scores.shape[0]
    # Create a NumPy index for scores on the pareto front (zero indexed)
    population_ids = np.arange(population_size)
    # Create a starting list of items on the Pareto front
    # All items start off as being labelled as on the Parteo front
    on_pareto_front = np.ones(population_size, dtype=bool)
    # Loop through each x. This will then be compared with ys
    for x in range(population_size):
        # Loop through all ys
        for y in range(population_size):
            # Check if our 'x' point is dominated by out 'y' point
            if all(scores[y] <= scores[x]) and any(scores[y] < scores[x]):
                # y dominates x. Label 'x' point as not on Pareto front
                on_pareto_front[x] = 0
                # Stop further comparisons with 'x' (no more comparisons needed)
                break

    # update pareto_front to contain only the coordinate pairs of points on the pareto front
    pareto_front = population_ids[on_pareto_front]
    pareto_front = scores[pareto_front]

    #put output in the same format as the input
    result = [tuple(row) for row in pareto_front]

    return result
