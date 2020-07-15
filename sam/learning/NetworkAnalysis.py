# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 16:13:58 2020

@author: samwa
"""

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt


def get_road_network(place_name, network_type='drive'):
    """
    
    Parameters
    ----------
    place_name : STRING
        A string of the location of the city in question.
    network_type : STRING, optional
        A string of the type of transportation. The default is 'drive'.

    Returns
    -------
    Map network of the road network at the specified location, and projections of the nodes as well

    """

    graph = ox.graph_from_place(place_name, network_type='drive')
  
    #project onto utm coordinates
    graph_proj = ox.project_graph(graph)
    
    fig, ax = ox.plot_graph(graph_proj)
    plt.tight_layout()
    
    nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
    
    return graph_proj, nodes_proj
    
    

def calculate_shortest_distance(orig_xy, target_xy, graph_proj, nodes_proj):
    """
    
    Parameters
    ----------
    orig_xy : TYPE
        DESCRIPTION.
    target_xy : TYPE
        DESCRIPTION.
    graph_proj : TYPE
        DESCRIPTION.
    nodes_proj : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    orig_node = ox.get_nearest_node(graph_proj, orig_xy, method='euclidean')
    target_node = ox.get_nearest_node(graph_proj, target_xy, method='euclidean')

    #calculate the shortest path using networkx modules
    shortest_route = nx.shortest_path(G=graph_proj, source=orig_node, target=target_node, weight='length')
    shortest_route_length = nx.shortest_path_length(G=graph_proj, source=orig_node, target=target_node)
    
    return shortest_route_length, shortest_route