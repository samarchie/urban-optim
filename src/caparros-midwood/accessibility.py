# -*- coding: utf-8 -*-
"""
Calculate_Accessibility 25/05/15
Author: Daniel Caparros-Midwood

To calculate the performance of a spatial plan for 𝑓𝑑𝑖𝑠𝑡 the Calculate Accessibility
module shown below is run prior to the operation to calculate the shortest path
distance between the defined CBD/ town centre and the possible development sites.
The shortest path from each possible development site is then recorded to be
referenced by the Evaluate module.

Intended for incorporation with the Spatial Optimisation Framework

Module calculates shortest path distance of a road network from cells
available for development to identified CBDs Module is preprocessed to produce
a lookup table to calculate fdist
"""

import networkx as nx # Network Analysis module to calculate shortest path
import rasterio # To handles spatial data
import numpy as np # Mathematical processing

def Generate_Development_Sites(Available_Sites, X,Y):
    """ Extract the available sites from which to calculate an accessibility measure.
    """
    Available_DevSites = []

    for x in range(0,X):
        for y in range(0,Y):
            site_yx = (y,x)
            if Available_Sites[site_yx] == 1:
                Available_DevSites.append(site_yx)

    return Available_DevSites

def Conv_2_Coords(list_of_sites, geo_t_params):
    """ Using the GDAL library to calculate the centroid of a coordinate
    """
    site_nodes = []
    for site in list_of_sites:
        y = site[0]
        x = site[1]
        # coord = coord of raster corner + (cell_coord * cell_size) + (cell_size/2)
        x_coord = geo_t_params[0] + (x*geo_t_params[1]) + (geo_t_params[1]/2)
        y_coord = geo_t_params[3] - (y*geo_t_params[1]) + (geo_t_params[5]/2)

        node_coord=(x_coord, y_coord)
        site_nodes.append(node_coord)
    return site_nodes

def calc_closest(new_node, node_list):
    """ Identify closest road node to connext to network
    """

    # Set initial distance to infinity
    best_gdist = float("inf")
    closest_node=[0,0]
    for comp_node in node_list.nodes():

        gdist = (abs(comp_node[0]-new_node[0])+abs(comp_node[1]-new_node[1]))
        if abs(gdist) <best_gdist:
            best_gdist = gdist
            # replaces the previus closest node
            closest_node = comp_node

    return closest_node

def Add_Edges(g, node, closest_node):
    """ Add node to the network then add an edge to connect it up to
    it's closest node
    """
    g.add_node(node)
    g.add_edge(node, closest_node)
    return g

def Add_Nodes_To_Network(node_list,network):
    """ Handles incorpating new nodes to the network
    Adds an edge between the node and the node calculated to be closest
    """
    for node in node_list:
        # Calculate the closest road node
        closest_node= calc_closest(node, network)
        network.add_node(node) #adds node to network
        network.add_edge(node,closest_node) #adds edge between nodes

def Calculate_Fitness(Development_Sites, CBD_Nodes, Road_Network, geo_t_params):
    """ Calcuates the shortest path for each available cell. The network is pre
    processed with the available dev sites converted to XY and added to the road
    network. The road network needs to be undirected.
    """
    # Convert sites to geographic centroid
    Dev_Nodes = Conv_2_Coords(Development_Sites, geo_t_params)

    Road_Network=Road_Network.to_undirected() #remove direction restrictions
    #Add CBD and development sites to the road network
    Add_Nodes_To_Network(CBD_Nodes, Road_Network)
    Add_Nodes_To_Network(Dev_Nodes, Road_Network)

    # Calcuate the shortest distance from each site to a CBD then return average
    fdist_list = []
    for Dev_Site in Dev_Nodes:
        # Initial shortest difference to infinity
        shrtst_dist=float("inf")
        for CBD in CBD_Nodes:
            # Calculate the shortest path to each CBD
            dist = nx.shortest_path_length(Road_Network,Dev_Site,CBD, weight='Dist')
            if dist<shrtst_dist:
                shrtst_dist=dist

            fdist_list.append(shrtst_dist)

    return fdist_list

def Calc_fdist(Data_Folder):
    """ Function sets in motion the calculating of a series of shortest path distances
    from the centroids of the available sites (in this case Available.tif) to their
    closest town centre. We upload the town centres and Road Network before
    extract the available development sites from which to calculate an accessibility
    measure. Returns a list of smallest paths. Then the calc_fdist can collect
    the smallest paths for their proposed development sites.

    """

    # Road network which forms the path
    Road_Network = nx.read_shp(Data_Folder+'Road_Network.shp')
    # The CBD point file which we are calculating the shortest path distance to
    CBD_Nodes = nx.read_shp(Data_Folder+'Town_Centres.shp')

    # Extracting the dataset for potential sites to calculate fdist from each one
    file_pointer = rasterIO.opengdalraster(Data_Folder+'Available.tif')
    Available = rasterIO.readrasterband(file_pointer,1)

    # Extracting the geotrans which is necessary for caluclating the centroids
    # of potential development sites
    d,X,Y,p,geotrans= rasterIO.readrastermeta(file_pointer)

    # Extract the cells which are available for development
    Sites_to_Calculate = Generate_Development_Sites(Available,X,Y)
    # geotrans used to calculate their XY value
    fdist_values = Calculate_Fitness(Sites_to_Calculate, CBD_Nodes, Road_Network, geotrans)

    np.savetxt(Data_Folder+'fdist_lookup.txt', fdist_values, delimiter = ',', )
