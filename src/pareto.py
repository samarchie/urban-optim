"""
24th of September 2020
Author: Sam Archie and Jamie Fleming

beep boop here some pretty graphs

"""

import geopandas as gpd
import matplotlib.pyplot as plt


def add_to_paretofront_set(paretofront_set, children):
    """

    """

    for child in children:
        if (child[2][0], child[2][1]) not in paretofront_set[0]:
            paretofront_set[0].append((child[2][0], child[2][1]))
        if (child[2][0], child[2][2]) not in paretofront_set[1]:
            paretofront_set[1].append((child[2][0], child[2][2]))
        if (child[2][0], child[2][3]) not in paretofront_set[2]:
            paretofront_set[2].append((child[2][0], child[2][3]))
        if (child[2][0], child[2][4]) not in paretofront_set[3]:
            paretofront_set[3].append((child[2][0], child[2][4]))
        if (child[2][0], child[2][5]) not in paretofront_set[4]:
            paretofront_set[4].append((child[2][0], child[2][5]))

        if (child[2][1], child[2][2]) not in paretofront_set[5]:
            paretofront_set[5].append((child[2][1], child[2][2]))
        if (child[2][1], child[2][3]) not in paretofront_set[6]:
            paretofront_set[6].append((child[2][1], child[2][3]))
        if (child[2][1], child[2][4]) not in paretofront_set[7]:
            paretofront_set[7].append((child[2][1], child[2][4]))
        if (child[2][1], child[2][5]) not in paretofront_set[8]:
            paretofront_set[8].append((child[2][1], child[2][5]))

        if (child[2][2], child[2][3]) not in paretofront_set[9]:
            paretofront_set[9].append((child[2][2], child[2][3]))
        if (child[2][2], child[2][4]) not in paretofront_set[10]:
            paretofront_set[10].append((child[2][2], child[2][4]))
        if (child[2][2], child[2][5]) not in paretofront_set[11]:
            paretofront_set[11].append((child[2][2], child[2][5]))

        if (child[2][3], child[2][4]) not in paretofront_set[12]:
            paretofront_set[12].append((child[2][3], child[2][4]))
        if (child[2][3], child[2][5]) not in paretofront_set[13]:
            paretofront_set[13].append((child[2][3], child[2][5]))

        if (child[2][4], child[2][5]) not in paretofront_set[14]:
            paretofront_set[14].append((child[2][4], child[2][5]))

    return paretofront_set


def plot_pareto_fronts(paretofront_set):
    """

    """
    fig, axs = plt.subplots(5, 3, figsize=[20, 20])
    subtitles = ['f_tsu vs f_cflood', 'f_tsu vs f_rflood', 'f_tsu vs f_liq', 'f_tsu vs f_dist', 'f_tsu vs f_dev', 'f_cflood vs f_rflood', 'f_cflood vs f_liq', 'f_cflood vs f_dist', 'f_cflood vs f_dev', 'rflood vs f_liq', 'rflood vs f_dist', 'rflood vs f_dev', 'f_liq vs f_dist', 'f_liq vs f_dev', 'f_dist vs f_dev']
    index = 0
    col = 0
    row = 0
    for objective_pair in paretofront_set:
        xs = [x[0] for x in objective_pair]
        ys = [y[1] for y in objective_pair]

        axs[row, col].scatter(xs, ys, marker='x')
        axs[row, col].set_title(subtitles[index])

        if col < 2:
            col += 1
        else:
            col = 0
            row += 1

        index += 1

    plt.show()
