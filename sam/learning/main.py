# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 10:59:08 2020

@author: samwa
"""


from NetworkAnalysis import *


def main():
    """ A main funtion; a place to call home! """

    graph_proj, nodes_proj = get_road_network('Christchurch', 'drive')
    
    orig_xy = (5682721.841129398, 368385.45834822085)
    target_xy = (5688766.504518856, 376909.34742367646)
    
    shortest_route_length, shortest_route = calculate_shortest_distance(orig_xy, target_xy, graph_proj, nodes_proj)
    
    fig, ax = ox.plot.plot_graph_route(graph_proj, shortest_route)
    plt.tight_layout()
    
    print("The shortest route is: " + str(shortest_route_length) + " km")

main()