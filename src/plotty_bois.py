"""
24th of September 2020
Author: Sam Archie and Jamie Fleming

beep boop here some pretty graphs

"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os, math
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import plotly.graph_objects as go
from copy import copy


def add_to_pareto_set(pareto_set, parents):
    """This module adds the parents from each generation to the pareto set. Takes all Development plans for this generation, and adds all parents to the pareto_set to be plotted later.
    Pareto set is essentially a list of all objective function combinations found in the GA

    Parameters
    ----------
    pareto_set : List
        A list of 15 nested lists. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points and the parent itself, which indicate an individual parents score against the two objective functions alongside the Individual Class.
    parents : List
        A list of NO_parent amounts of lists. Each list contains an index value and three nested lists. The first lists represents the modelled increase in density (dwellings per hectare) for each statistical area - in the order of the inputted census GeoDataFrame. The second nested list represents the modelled increase in dwellings for each statistical area - in the order of the inputted census GeoDataFrame as well.The third nested list represents the scores of the parent against each objective function and the overall F-score.

    Returns
    -------
    pareto_set : List
        A list of 15 nested lists, updated with parents from a generation. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions alongside the Individual Class.

    """

    # Iterate through all current development plans
    for parent in parents:
        # Check if each unique objective pair has been added yet, and add it if not

        #f_scores= (f_tsu, f_cflood, f_rflood, f_liq, f_dist, f_dev)
        f_scores = parent.fitness.values

        if (f_scores[0], f_scores[1]) not in pareto_set[0]:
            pareto_set[0].append((f_scores[0], f_scores[1], parent))
        if (f_scores[0], f_scores[2]) not in pareto_set[1]:
            pareto_set[1].append((f_scores[0], f_scores[2], parent))
        if (f_scores[0], f_scores[3]) not in pareto_set[2]:
            pareto_set[2].append((f_scores[0], f_scores[3], parent))
        if (f_scores[0], f_scores[4]) not in pareto_set[3]:
            pareto_set[3].append((f_scores[0], f_scores[4], parent))
        if (f_scores[0], f_scores[5]) not in pareto_set[4]:
            pareto_set[4].append((f_scores[0], f_scores[5], parent))

        if (f_scores[1], f_scores[2]) not in pareto_set[5]:
            pareto_set[5].append((f_scores[1], f_scores[2], parent))
        if (f_scores[1], f_scores[3]) not in pareto_set[6]:
            pareto_set[6].append((f_scores[1], f_scores[3], parent))
        if (f_scores[1], f_scores[4]) not in pareto_set[7]:
            pareto_set[7].append((f_scores[1], f_scores[4], parent))
        if (f_scores[1], f_scores[5]) not in pareto_set[8]:
            pareto_set[8].append((f_scores[1], f_scores[5], parent))

        if (f_scores[2], f_scores[3]) not in pareto_set[9]:
            pareto_set[9].append((f_scores[2], f_scores[3], parent))
        if (f_scores[2], f_scores[4]) not in pareto_set[10]:
            pareto_set[10].append((f_scores[2], f_scores[4], parent))
        if (f_scores[2], f_scores[5]) not in pareto_set[11]:
            pareto_set[11].append((f_scores[2], f_scores[5], parent))

        if (f_scores[3], f_scores[4]) not in pareto_set[12]:
            pareto_set[12].append((f_scores[3], f_scores[4], parent))
        if (f_scores[3], f_scores[5]) not in pareto_set[13]:
            pareto_set[13].append((f_scores[3], f_scores[5], parent))

        if (f_scores[4], f_scores[5]) not in pareto_set[14]:
            pareto_set[14].append((f_scores[4], f_scores[5], parent))

    return pareto_set


def plot_pareto_plots(pareto_set, scheme, NO_parents, NO_generations):
    """This module plots both the pareto plots and the pareto-front plots.

    Parameters
    ----------
    paretofront_set : List
        A list of 15 nested lists, updated with parents from a generation. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions alongside the Individual Class.
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    NO_generations : Integer
        User specified parameter for hor many generations occur as part of the gentic algorithm.

    Returns
    -------
    None

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
    obj_funcs = [r"$normalised  f_{tsu}$", r"$normalised  f_{cflood}$", r"$normalised  f_{rflood}$", r"$normalised  f_{liq}$", r"$normalised  f_{dist}$", r"$normalised  f_{dev}$"]

    #set up subplot subtitles
    subtitles = ['f_tsu vs f_cflood', 'f_tsu vs f_rflood', 'f_tsu vs f_liq', 'f_tsu vs f_dist', 'f_tsu vs f_dev', 'f_cflood vs f_rflood', 'f_cflood vs f_liq', 'f_cflood vs f_dist', 'f_cflood vs f_dev', 'f_rflood vs f_liq', 'f_rflood vs f_dist', 'f_rflood vs f_dev', 'f_liq vs f_dist', 'f_liq vs f_dev', 'f_dist vs f_dev']

    # Set up plot indexes so we know where to plot each objective pair
    # these will iterate
    index = 0
    col = 0
    row = 0

    for objective_pair in pareto_set:

        #Find the Individuals that are on the pareto-front, which are the optimal parents as they dominate in one of the objectives
        pareto_front = identify_pareto_front(objective_pair)
        pareto_front.sort()

        # Create x and y coordinates for each objective pair
        xs1 = [x[0] for x in objective_pair]
        ys1 = [y[1] for y in objective_pair]

        #Find which points are on objective front, and assign their x and y coordinates in a plotable format
        xs2 = [x[0] for x in pareto_front]
        ys2 = [y[1] for y in pareto_front]

        # Normalise plots by the maximum seen
        xs2 = xs2/np.max(xs1)
        ys2 = ys2/np.max(ys1)
        xs1 = xs1/np.max(xs1)
        ys1 = ys1/np.max(ys1)

        #Plot a marker representing each Individual
        axs[row, col].scatter(xs1, ys1, marker='x')
        #Plot a curve linking the Individuals on the pareto-front
        axs[row, col].plot(xs2, ys2, color='red')
        #Set the axis limits from 0 to 1, as we have normalised the data
        axs[row, col].set(xlim=(0, 1), ylim=(0, 1))

        #Set x and y axis labels based on what subplot we are currently in
        if index < 5:
            axs[row, col].set_xlabel(obj_funcs[0])
            axs[row, col].set_ylabel(obj_funcs[index+1])
        elif index < 9:
            axs[row, col].set_xlabel(obj_funcs[1])
            axs[row, col].set_ylabel(obj_funcs[index-3])
        elif index < 12:
            axs[row, col].set_xlabel(obj_funcs[2])
            axs[row, col].set_ylabel(obj_funcs[index-6])
        elif index < 14:
            axs[row, col].set_xlabel(obj_funcs[3])
            axs[row, col].set_ylabel(obj_funcs[index-8])
        else:
            axs[row, col].set_xlabel(obj_funcs[4])
            axs[row, col].set_ylabel(obj_funcs[index-9])

        #Logic to keep track of which plot we are up to
        if col < cols-1:
            col += 1
        else:
            col = 0
            row += 1

        #Now we want to add to the pareto front plots as welL!
        fig2, axs2 = add_to_pareto_fronts_plots((xs2, ys2), fig2, axs2, subtitles[index])

        index += 1

    # Save the figure detailing all Inidividals and the pareto front
    fig.savefig("fig/{}/pareto_plots_par={}_gens={}.pdf".format(scheme ,NO_parents, NO_generations), transparent=False, dpi=600)

    #Assign axis labels and limits for each of the subplots
    counter = 0
    for row in range(0, rows2):
        for col in range(0, cols2):
            axs2[row, col].set(xlabel='f', ylabel='{}'.format(obj_funcs[counter]))
            axs2[row, col].set(xlim=(0, 1), ylim=(0, 1))
            counter += 1

    #Position the legend at the top center of the figure, using the bbox command, and this will save there being a legend for each of the 6 subplots!
    labels = obj_funcs[1:] + obj_funcs[:1]
    fig2.legend(labels=labels, loc='upper center', ncol=6, mode="expand", borderaxespad=12)    # Save the figure detailing all Inidividals and the pareto front
    fig2.savefig("fig/{}/pareto_fronts_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations), transparent=False, dpi=600)


def identify_pareto_front(objective_pair):
    """This module evaluates the pareto set of all data points for the two objective functions, and returns a tuple of points that represent the pareto front of the data set.

    Parameters
    ----------
    objective_pair : List of tuples
        The list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points and the parent itself, which indicate an individual parents score against the two objective functions alongside the Individual Class.

    Returns
    -------
    pareto_front : List of tuples
        The list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points and the parent itself, which indicate an individual parents score against the two objective functions alongside the Individual Class.
    """

    #Convert the list of tuples of (f_score1, f_score2, parent) into an array of tuples
    scores_raw = np.asarray(objective_pair)
    #Only save the (f_score1, f_score2) into a new list instead of modifying the raw list
    scores_modified = []
    for score_raw in scores_raw:
        #copy over the f-score values, and not the parent!
        scores_modified.append(score_raw[:-1])

    #Turn the list into an array
    scores = np.asarray(scores_modified)
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
    pareto_front = scores_raw[pareto_front]

    #put output in the same format as the input
    pareto_front = [tuple(row) for row in pareto_front]

    return pareto_front


def add_to_pareto_fronts_plots(data, fig2, axs2, pareto_set_names):
    """This module adds a pareto plot of two objective functions to the pareto front plot..

    Parameters
    ----------
    data : Tuple
        A tuple of the two f_score values from the pareto set, in the form of (xs2, ys2), where xs2 and xs2 are lists of the same length.
    fig2 : Figure
        A matplotlib.pyplot Figure, that contains many subplots that may or may not be empty. This Figure represents that the tradeoff curves of one function .
    axs2 : axes.Axes
        A matplotlib.pyplot Axes, that has many sub-axes that may or may not be empty. This Axis represents that spatial variations of specificied generation's parents.
    pareto_set_names : List of Strings
        A list of strings of the objective function tradeoffs, in the order of the axis of the plot.

    Returns
    -------
    fig2 : Figure
        A matplotlib.pyplot Figure, that contains many subplots that may or may not be empty. This Figure represents that the tradeoff curves of one function .
    axs2 : axes.Axes
        A matplotlib.pyplot Axes, that has many sub-axes that may or may not be empty. This Axis represents that spatial variations of specificied generation's parents.

    """

    #Set up subplot axis titles (y-axis)
    obj_funcs = ["f_tsu", "f_cflood", "f_rflood", "f_liq", "f_dist", "f_dev"]

    #Set up how the axis are to be made (what order the axes go in) and what colours lines are each objective function.
    plot_layout = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    plot_colours = ["#85d4ff", "#540b0e", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"]

    #Figure out what objectives we have and and put them in the right plot axis and column! This will be in the form of ["f_tsu", "vs", "f_cflood"] for example os only need to check the 1st and 3rd item.
    pareto_names = pareto_set_names.split(" ")

    #Go through each objective function name to see to see if [out of the total 6 objective functions] if the pareto_set of two battling objectives is present.
    for title_index in range(0, len(obj_funcs)):

        title = obj_funcs[title_index]

        if pareto_names[0] == title:
            #Then we have the thing we want first (eg need to swap the x and y coordinates as we want to plot the f function on the y axis!)
            ys2, xs2 = data

            #grab the right place to put the plot
            row, col = plot_layout[title_index]

            #and we also need to find which colour to make the line (as its based on the other objective function)
            other_index = obj_funcs.index(pareto_names[2])
            color = plot_colours[other_index]

            if plot_layout[title_index] == (1, 1):
                # Yay let make pretty picture
                axs2[row, col].plot(xs2, ys2, color=color, label=pareto_names[2])

            else:
                # Yay let make pretty picture
                axs2[row, col].plot(xs2, ys2, color=color)


        elif pareto_names[2] == title:
            #The the data is the right way around for plotting!
            xs2, ys2 = data

            #grab the right place to put the plot
            row, col = plot_layout[title_index]

            #and we also need to find which colour to make the line (as its based on the other objective function)
            other_index = obj_funcs.index(pareto_names[0])
            color = plot_colours[other_index]

            if plot_layout[title_index] == (1, 1):
                # Yay let make pretty picture
                axs2[row, col].plot(xs2, ys2, color=color, label=pareto_names[0])

            else:
                # Yay let make pretty picture
                axs2[row, col].plot(xs2, ys2, color=color)


    return fig2, axs2


def plot_development_sites(parents, gen_number, when_to_plot, census, scheme, fig_spatial=None, axs_spatial=None):
    """This modules takes a set of parents at a specified generation number, and adds it spatial development plan (d's) to a figure. This is used to showcase how the genetic algorithm should converge on superior sites.

    Parameters
    ----------
    parents : List of Individuals
        A list of the best Individuals at the end of a generation.
    gen_number : Integer
        Integer of the generation number that has just occured.
    when_to_plot : Generator/Range/List
        List of intergers, that represent when to halt the genetic algorithm and plot the spatial development of the current parents.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.
    fig_spatial : Figure
        A matplotlib.pyplot Figure, that contains many subplots that may or may not be empty. This Figure represents that spatial variations of specificied generation's parents.
    axs_spatial : axes.Axes
        A matplotlib.pyplot Axes, that has many sub-axes that may or may not be empty. This Axis represents that spatial variations of specificied generation's parents.

    Returns
    -------
    fig_spatial : Figure
        A matplotlib.pyplot Figure, that contains many subplots that may or may not be empty. This Figure represents that spatial variations of specificied generation's parents.
    axs_spatial : axes.Axes
        A matplotlib.pyplot Axes, that has many sub-axes that may or may not be empty. This Axis represents that spatial variations of specificied generation's parents.

    """

    #Check to see if we have made a blank plot or not!
    if fig_spatial == None and axs_spatial == None:
        #Then we have not set up our subplots yet, and hence we should do so!
        number_of_subplots = len(when_to_plot)

        # set up subplots for pareto plots (all markers and front)
        fig_spatial, axs_spatial = plt.subplots(number_of_subplots, 1, figsize=[20, 20])
        fig_spatial.suptitle('Development Sites representing selected parents sets')

    #Create an array where each index represents the original census (in order) and is assigned a True or False Value based on if one of the parents develops on it. Assume all properties are not built on, and check to see if they are.
    is_developed = np.zeros(len(parents[0]), dtype=np.bool)
    for parent in parents:
        #Got through each property one by one in each parent, and see if its developed
        for prop_index in range(0, len(is_developed)):

            if not is_developed[prop_index]:
                #Then the propety we are looking at has NOT been developed on by previous parents. Check to see if this parent does build on the site and update the master list with the answer found!
                is_developed[prop_index] = parent[prop_index] != 0

    #Now we want to plot which development sites have been built on!
    sites_built_on = census[is_developed]

    if len(when_to_plot) > 1:
        #Then there are mutiple times that the user has specified to plot, and hence it is a multi axis figure
        #Find which plot to put it on (eg axis) by finding how far through we are of the ploting
        row_number = list(when_to_plot).index(gen_number)
        #Plot the development sites on the axis
        sites_built_on.plot(ax=axs_spatial[row_number])
        census.boundary.plot(ax=axs_spatial[row_number], color='black', linewidth=1, alpha=0.20)
        axs_spatial[row_number].set_title('Generation {}'.format(gen_number))

    else:
        #Then the user has specified only this one generation to plot!
        #Plot the development sites on the axis
        sites_built_on.plot(ax=axs_spatial)
        census.boundary.plot(ax=axs_spatial, color='black', linewidth=1, alpha=0.20)
        axs_spatial.set(title='Generation {}'.format(gen_number))

    #if this is the last generation to plot, then we shall save the figure appropiately!
    if gen_number == when_to_plot[-1]:
        plt.tight_layout()
        plt.savefig("fig/{}/all_development_sites_par={}_gens={}.pdf".format(scheme, len(parents), gen_number), transparent=False, dpi=600)

    return fig_spatial, axs_spatial


def plot_ranked_pareto_sites(pareto_set, census, MOPO_List, scheme, NO_parents, NO_generations):
    """This module creates a plot that showcases the average percentage of dwellings that are associated with a statistical area over the entire pareto set (which is the suprerior parents).

    Parameters
    ----------
    pareto_set : List
        A list of 15 nested lists, updated with parents from a generation. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions alongside the Individual Class.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    NO_generations : Integer
        User specified parameter for hor many generations occur as part of the gentic algorithm.

    Returns
    -------
    None

    """

    #Firstly, create the figure and axes to whihc we will plot on
    fig, ax = plt.subplots(1, 1, figsize=[20, 20])

    #Create a blank list, to where we will put all the parents on the pareto front curve in
    pareto_front_parents = []

    #Go through each objective pair (eg f_dist vd f_dev) in the pareto plot one at a time
    for objective_pair in pareto_set:
        #Find all the points (and associated parents) on the pareto-front curve
        pareto_front = identify_pareto_front(objective_pair)

        for point in pareto_front:
            #point = (f_score1, f_score2, parent_Individual)
            #Extract the parent from each point on the paretofront curve and add it to the list of pareto parents if it is not already in there
            if point[-1] not in pareto_front_parents:
                pareto_front_parents.append(point[-1])

    #Now we have all the parents on the pareto fronts!
    #We want to keep track of the rolling sum of  allocations in each ststaistical area, so we have to zero the list to start with
    sum_allocation = [0] * len(census)
    MOPO_sols_found = 0

    #Now we want to go through each parent on the pareto_front and calculate the percentge allocation of buildings to each statistical area
    for parent in pareto_front_parents:

        # #The amount of dwellings might not actaully be bang on 30,000 (or whatever was inputted) as the cross-over & mutation operators could have changed that.
        # dwellings_sum = sum(parent)
        for obj_function_list in MOPO_List:
            MOPO_sols_found += len(obj_function_list)

            if parent in obj_function_list:

                for index in range(0, len(parent)):
                    prop = parent[index]

                    if prop != 0:

                        sum_allocation[index] += 1

    #Take the rolling sums list of percentages and average/normalise it, such that the highest allocation is now 100%.
    percentage_allocation = [x / MOPO_sols_found for x in sum_allocation]

    #We want to have a colourbar that indicates a sclae of the allocation proprtion in each statistical area. The following code makes it all happen!
    norm = colors.Normalize(vmin=0, vmax=100)
    cbar = plt.cm.ScalarMappable(norm=norm, cmap='Blues')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    ax_cbr = fig.colorbar(cbar, ax=ax, cax=cax, label="Percentage Allocation")

    #Add the percentage to the census dataframe as a column
    census = add_column_to_census(census, percentage_allocation, "% allocation")

    #Plot the percentages againgst the statistical areas (which are thin opaque boundary lines)
    census.plot(column='% allocation', cmap="Blues", legend=False, ax=ax)
    census.boundary.plot(ax=ax, color='black', linewidth=1, alpha=0.20)

    #Tidy up the figure and save it
    ax.set_title('Ranked Pareto-Optimal Development Sites after {} generations'.format(NO_generations))
    plt.tight_layout()
    plt.savefig("fig/{}/pareto_development_sites_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations), transparent=False, dpi=600)


def add_column_to_census(census, data_to_add, column_name):
    """Ths module creates a new column to GeoDataFrame and append data to it in the same order.

    Parameters
    ----------
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.
    data_to_add : List
        A list of floating point numbers which are in the same order as the GeoDataFrame from top to bottom.
    column_name : String
        The title of the column to be created.

    Returns
    -------
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score. An extra column exists with the newly inputted data as well.

    """

    #Convert the census array to a dictionary so that we can add values
    census_array = census.to_numpy()
    census_list = np.ndarray.tolist(census_array)
    census_dict = { census_list[i][0] : census_list[i][1:] for i in range(0, len(census_list)) }

    #Add the f-function values to the dictionary of the parcels
    index = 0
    for key, value in census_dict.items():
        value.append(float(data_to_add[index]))
        index += 1

    #Convert the merged dictionry back to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(census_dict, orient='index', dtype=object)
    proc_census = gpd.GeoDataFrame(df)

    #Add the statistical area mesh area number to a columns
    proc_census["SA index"] = proc_census.index

    #clean up the GeoDataFrame and we're good to go!
    current_columns = census.columns.values.tolist()
    updated_column_names = current_columns[1:] + [column_name, "SA index"]

    proc_census.columns = pd.Index(updated_column_names)

    proc_census = proc_census[updated_column_names[-1:] + updated_column_names[:-1]]

    proc_census.set_geometry(col='geometry', inplace=True)
    proc_census.set_crs("EPSG:2193", inplace=True)

    return proc_census


def plot_MOPO_plots(MOPO_List, census, scheme, NO_parents, NO_generations):
    """This module creates plots that showcase the spatially optimal locations to build when addressing each individual objective function seperately, and another plot showing the tradeoffs between these individually superior Individuals.

    Parameters
    ----------
    MOPO_List : List of Lists
        A list of 6 lists, where each nested list represents an objective functions, such as f_dist. In each of these nested lists is Individuals which have been evaliated to be the best seen for that objective at the present time. It is not replaced when a better Individual is found, but rather the new and better one is appended to the back of the list.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score. An extra column exists with the newly inputted data as well.
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    NO_generations : Integer
        User specified parameter for hor many generations occur as part of the gentic algorithm.

    Returns
    -------
    None

    """

    #set up a normal line plot using the overalpping lines of the f_score values of each MOPO parent
    fig, axs = plt.subplots(1, 1, figsize=[20, 10])
    fig.suptitle('Performance of the best Pareto-optimal spatial plans across the range of objectives')

    #set up a radar-chart/spiderweb plot using the Plotly module that has circles of the f_score values of each MOPO parent
    fig_radial = go.Figure()

    #Set up plot that will contain the spatial layout of each MOPO parent
    fig2, axs2 = plt.subplots(3, 2, figsize=[20, 20])
    fig2.suptitle('Best Pareto-optimal spatial plans across the range of objectives')

    #Set up subplot axis titles (y-axis)
    obj_funcs = [r"$f_{tsu}$", r"$f_{cflood}$", r"$f_{rflood}$", r"$f_{liq}$", r"$f_{dist}$", r"$f_{dev}$"]

    #Set up subplot axis titles (y-axis)
    obj_funcs_min = [r"$min f_{tsu}$", r"$min f_{cflood}$", r"$min f_{rflood}$", r"$min f_{liq}$", r"$min f_{dist}$", r"$min f_{dev}$"]

    #List in what order the plot shall be in (eg left to right in this case)
    plot_layout = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    plot_colours = ["#003049", "#540b0e", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"]

    #When we specify the axis limits at the end, we will need to know the highest f score seen (y max limit)
    max_score_seen = 0

    #Go through each of the superior developments plans for each objective functions
    for index in range(0, len(MOPO_List) - 1):
        #Extract the superior developments plans in question
        obj_fnc_MOPOs = MOPO_List[index]

        #The best parent seen is the last one in the list!
        best_parent = obj_fnc_MOPOs[-1]

        #f_scores= (f_tsu, f_cflood, f_rflood, f_liq, f_dist, f_dev)
        f_scores = best_parent.fitness.values

        #Check to see if it contains a new highest f_score value!
        if max(f_scores) > max_score_seen:
            max_score_seen = max(f_scores)

        #Plot MOPO line againgst the objective functions for the radar chart
        fig_radial.add_trace(go.Scatterpolar(r=list(f_scores), theta=obj_funcs, fill='toself', name=obj_funcs_min[index]))

        #Plot MOPO line againgst the objective functions for the normal line plot
        axs.plot([0, 1, 2, 3, 4, 5], f_scores, color=plot_colours[index], label=obj_funcs[index])

        #Create a of Trues and Falses which indicate for which statistical areas are built on (in the same order as the census)
        bool_array = np.asarray(best_parent) != 0
        #Extract only the staistical areas that are to densified
        props_developed_on = census[list(bool_array)]

        #Figure out what subplot we should plot on!
        placement = plot_layout[index]

        #Plot the staistical areas that are to densified, and also the bondaries of all statistical areas as well
        props_developed_on.plot(ax=axs2[placement])
        census.boundary.plot(ax=axs2[placement], color='black', linewidth=1, alpha=0.20)

        #Set th subplots title to tell ther viewer which objective function this is for!
        axs2[placement].set_title("min " + obj_funcs[index])

    # Format the axes of the MOPO tradeoff plot (the one with 6 squiggly overlapping lines) to actually be strings of the objetive funcation names instead of values between 0 and 6
    axs.set_xticklabels([obj_funcs[0]] + obj_funcs, fontdict=None, minor=False)

    #Tidy up the plot and then save the figure
    axs.set_yticks(np.arange(0, 1.1*max_score_seen, step=1000))
    axs.legend(obj_funcs_min, loc="best")
    axs.set_ylabel("Total Objective Score")
    fig.tight_layout()
    fig.savefig("fig/{}/mopo_tradeoffs_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations), transparent=False, dpi=600)

    #Set the axis and titles for the radar chart
    title_settings = {'text': "Performance of the best Pareto-optimal spatial plans"}
    fig_radial.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0, max_score_seen])), showlegend=True, title=title_settings)
    #Save the radar chart
    fig_radial.write_image("fig/{}/mopo_tradeoffs_radial_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations))

    #And for the best MOPO sites plot, just tidy it up a bit and save it!
    fig2.tight_layout()
    fig2.savefig("fig/{}/best_mopo_sites_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations), transparent=False, dpi=600)


def save_ranked_F_score_sites(parents, census, toolbox, scheme, NO_parents, NO_generations):
    """This module creates a plot that showcases the average percentage of dwellings that are associated with a statistical area over the entire pareto set (which is the suprerior parents).

    Parameters
    ----------
    pareto_set : List
        A list of 15 nested lists, updated with parents from a generation. Each list represents a tradeoff between two individual objective functions, such as flooding vs distance. The list for each tradeoff contains a tuple of points, which indicate an individual parents score against the two objective functions alongside the Individual Class.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions, and one for the combined objective functions score.
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    NO_generations : Integer
        User specified parameter for how many generations occur as part of the gentic algorithm.

    Returns
    -------
    None

    """

    #Firstly, create the figure and axes to whihc we will plot on
    fig, ax = plt.subplots(1, 1, figsize=[20, 20])

    solutions = copy(parents)
    solutions.sort(key=lambda x: x.fitness.values[-1])


    threshold = 0.01 #takes the top 1 per cent
    number_to_pick = math.ceil(threshold * len(parents))

    best_parents = solutions[:number_to_pick]

    #We want to keep track of the rolling sum of  allocations in each ststaistical area, so we have to zero the list to start with
    sum_allocation = [0] * len(census)

    #Now we want to go through each parent on the pareto_front and calculate the percentge allocation of buildings to each statistical area
    for parent in best_parents:

        for index in range(0, len(parent)):

            prop = parent[index]
            if prop != 0:
                sum_allocation[index] += 1

    #Take the rolling sums list of percentages and average/normalise it, such that the highest allocation is now 100%.
    percentage_allocation = [x / len(best_parents) for x in sum_allocation]

    #We want to have a colourbar that indicates a sclae of the allocation proprtion in each statistical area. The following code makes it all happen!
    norm = colors.Normalize(vmin=0, vmax=100)
    cbar = plt.cm.ScalarMappable(norm=norm, cmap='Blues')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    ax_cbr = fig.colorbar(cbar, ax=ax, cax=cax, label="Percentage Allocation")

    #Add the percentage to the census dataframe as a column
    census = add_column_to_census(census, percentage_allocation, "F score %")

    #Plot the percentages againgst the statistical areas (which are thin opaque boundary lines)
    census.plot(column='F score %', cmap="Blues", legend=False, ax=ax)
    census.boundary.plot(ax=ax, color='black', linewidth=1, alpha=0.20)

    census.to_file("data/final/{}, {} parents and {} generations".format(scheme, NO_parents, NO_generations))

    #Tidy up the figure and save it
    ax.set_title('Averaged Top {}% of Development Sites after {} generations'.format(threshold*100, NO_generations))
    plt.tight_layout()
    plt.savefig("fig/{}/top_F_score_development_sites_par={}_gens={}.pdf".format(scheme, NO_parents, NO_generations), transparent=False, dpi=600)
