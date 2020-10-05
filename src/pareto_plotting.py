"""
24th of September 2020
Author: Sam Archie and Jamie Fleming

beep boop here some pretty graphs

"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os


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

        #f_scores= (f_tsu, f_cflood, f_rflood, f_liq, f_dist, f_dev)
        f_scores = parent.fitness.values

        if (f_scores[0], f_scores[1]) not in pareto_set[0]:
            pareto_set[0].append((f_scores[0], f_scores[1]))
        if (f_scores[0], f_scores[2]) not in pareto_set[1]:
            pareto_set[1].append((f_scores[0], f_scores[2]))
        if (f_scores[0], f_scores[3]) not in pareto_set[2]:
            pareto_set[2].append((f_scores[0], f_scores[3]))
        if (f_scores[0], f_scores[4]) not in pareto_set[3]:
            pareto_set[3].append((f_scores[0], f_scores[4]))
        if (f_scores[0], f_scores[5]) not in pareto_set[4]:
            pareto_set[4].append((f_scores[0], f_scores[5]))

        if (f_scores[1], f_scores[2]) not in pareto_set[5]:
            pareto_set[5].append((f_scores[1], f_scores[2]))
        if (f_scores[1], f_scores[3]) not in pareto_set[6]:
            pareto_set[6].append((f_scores[1], f_scores[3]))
        if (f_scores[1], f_scores[4]) not in pareto_set[7]:
            pareto_set[7].append((f_scores[1], f_scores[4]))
        if (f_scores[1], f_scores[5]) not in pareto_set[8]:
            pareto_set[8].append((f_scores[1], f_scores[5]))

        if (f_scores[2], f_scores[3]) not in pareto_set[9]:
            pareto_set[9].append((f_scores[2], f_scores[3]))
        if (f_scores[2], f_scores[4]) not in pareto_set[10]:
            pareto_set[10].append((f_scores[2], f_scores[4]))
        if (f_scores[2], f_scores[5]) not in pareto_set[11]:
            pareto_set[11].append((f_scores[2], f_scores[5]))

        if (f_scores[3], f_scores[4]) not in pareto_set[12]:
            pareto_set[12].append((f_scores[3], f_scores[4]))
        if (f_scores[3], f_scores[5]) not in pareto_set[13]:
            pareto_set[13].append((f_scores[3], f_scores[5]))

        if (f_scores[4], f_scores[5]) not in pareto_set[14]:
            pareto_set[14].append((f_scores[4], f_scores[5]))

    return pareto_set


def plot_pareto_plots(pareto_set, NO_parents, NO_generations):
    """
    pretty self explanatory tbh
    """

    # set up subplots for pareto plots (all markers and front)
    rows = 5 # Number of rows of subplots
    cols = 3 # Number of columns of subplots
    fig, axs = plt.subplots(rows, cols, figsize=[20, 20])
    fig.suptitle('Pareto Plots')

    # set up subplots for pareto front plots
    rows2 = 3 # Number of rows of subplots
    cols2 = 2 # Number of columns of subplots
    fig2, axs2 = plt.subplots(rows2, cols2, figsize=[20, 20])
    fig2.suptitle('Pareto Front Plots')

    #Set up subplot axis titles (y-axis)
    obj_funcs = [r"$f_{tsu}$", r"$f_{cflood}$", r"$f_{rflood}$", r"$f_{liq}$", r"$f_{dist}$", r"$f_{dev}$"]

    #set up subplot subtitles
    subtitles = ['f_tsu vs f_cflood', 'f_tsu vs f_rflood', 'f_tsu vs f_liq', 'f_tsu vs f_dist', 'f_tsu vs f_dev', 'f_cflood vs f_rflood', 'f_cflood vs f_liq', 'f_cflood vs f_dist', 'f_cflood vs f_dev', 'f_rflood vs f_liq', 'f_rflood vs f_dist', 'f_rflood vs f_dev', 'f_liq vs f_dist', 'f_liq vs f_dev', 'f_dist vs f_dev']

    # Set up plot indexes so we know where to plot each objective pair
    # these will iterate
    index = 0
    col = 0
    row = 0

    for objective_pair in pareto_set:

        pareto_front = identify_pareto_front(objective_pair)
        pareto_front.sort()

        # Create x and y coordinates for each objective pair
        xs1 = [x[0] for x in objective_pair]
        ys1 = [y[1] for y in objective_pair]

        #Find which points are on objective front, and assign their x and y coordinates in a plotable format
        xs2 = [x[0] for x in pareto_front]
        ys2 = [y[1] for y in pareto_front]

        # Normalise plots
        xs2 = xs2/np.max(xs1)
        ys2 = ys2/np.max(ys1)
        xs1 = xs1/np.max(xs1)
        ys1 = ys1/np.max(ys1)

        # Yay let make pretty picture
        axs[row, col].scatter(xs1, ys1, marker='x')
        axs[row, col].plot(xs2, ys2, color='red')
        # axs[row, col].set_title(subtitles[index])
        axs[row, col].set(xlim=(0, 1), ylim=(0, 1))

        if index < 5:
            axs[row, col].set_xlabel(obj_funcs[0])
            axs[row, col].set_ylabel(obj_funcs[index+1])
        elif index < 9:
            axs[row, col].set_xlabel(obj_funcs[1])
            axs[row, col].set_ylabel(obj_funcs[index-4])
        elif index < 12:
            axs[row, col].set_xlabel(obj_funcs[2])
            axs[row, col].set_ylabel(obj_funcs[index-7])
        elif index < 14:
            axs[row, col].set_xlabel(obj_funcs[3])
            axs[row, col].set_ylabel(obj_funcs[index-9])
        else:
            axs[row, col].set_xlabel(obj_funcs[4])
            axs[row, col].set_ylabel(obj_funcs[index-10])

        #Logic to keep track of which plot we are up to
        if col < cols-1:
            col += 1
        else:
            col = 0
            row += 1

        #Now we want to add to the pareto front plots as welL!
        fig2, axs2 = add_to_pareto_fronts_plots((xs2, ys2), fig2, axs2, subtitles[index])

        index += 1

    # Save figures
    fig.savefig("fig/pareto_plots_par={}_gens={}.png".format(NO_parents, NO_generations), transparent=False, dpi=600)

    counter = 0
    for row in range(0, rows2):
        for col in range(0, cols2):

            axs2[row, col].set(xlabel='f', ylabel='{}'.format(obj_funcs[counter]))
            axs2[row, col].set(xlim=(0, 1), ylim=(0, 1))
            axs2[row, col].legend(obj_funcs)

    fig2.savefig("fig/pareto_fronts_par={}_gens={}.png".format(NO_parents, NO_generations), transparent=False, dpi=600)


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


def add_to_pareto_fronts_plots(data, fig2, axs2, pareto_set_names):

    #Set up subplot axis titles (y-axis)
    obj_funcs = ["f_tsu", "f_cflood", "f_rflood", "f_liq", "f_dist", "f_dev"]

    plot_layout = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    plot_colours = ["#003049", "#540b0e", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"]

    #Figure out what objectives we have and and put them in the right plot axis and column!
    # print(pareto_set_names)
    pareto_names = pareto_set_names.split(" ")

    for title_index in range(0, len(obj_funcs)):

        title = obj_funcs[title_index]

        if pareto_names[0] == title:
            #Then we have the thing we want first (eg need to swap the x and y coordinates as we want to plot the f function on the y axis!)
            ys2, xs2 = data

            row, col = plot_layout[title_index]

            other_index = obj_funcs.index(pareto_names[2])
            color = plot_colours[other_index]

            # Yay let make pretty picture
            axs2[row, col].plot(xs2, ys2, color=color)



        elif pareto_names[2] == title:
            #The the data is the right way around for plotting!
            xs2, ys2 = data

            row, col = plot_layout[title_index]

            other_index = obj_funcs.index(pareto_names[0])
            color = plot_colours[other_index]

            # Yay let make pretty picture
            axs2[row, col].plot(xs2, ys2, color=color)


    return fig2, axs2
