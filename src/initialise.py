# -*- coding: utf-8 -*-
"""
29th of July 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 1 of the genetic algorthm. All data will be imported and pre-processed.

"""

#Import external modules
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as osm
import networkx as nx
import gdal
import rasterio as rio
import os
import numpy as np

Data_Folder = 'data/raw/'

def get_data():
    """This module gathers the data files from the user.

    Returns
    -------
    boundary
        A GeoDataFrame of the city boundary.
    roads
        A GeoDataFrame of the centre line of the road network
    hazards
        A list of GeoDataFrames of all the hazards to use
    census
        A GeoDataFrame of the census statistical areas of the region

    """

    boundary = gpd.read_file("data/boundary/city_boundary.shp")
    census = gpd.read_file(Data_Folder + "socioeconomic/2018-census-christchurch.shp")
    roads = gpd.read_file(Data_Folder + "infrastructure/street_centre_line.shp")
    hazards = [gpd.read_file(Data_Folder+ "/hazards/extreme_sea_level/esl_aep1_slr0.shp")]

    return boundary, roads, census, hazards


def clip_to_boundary(boundary_polygon, road_data, census_data, hazards_list):
    """Short summary.

    Parameters
    ----------
    boundary_polygon : GeoDataFrame
        Polygon of the city boundary.
    census_data : GeoDataFrame
        Census (2018) data of the smallest statistical areas.
    hazards_list : List of GeoDataFrames
        List of all hazards to be examined.

    Returns
    -------
    clipped_census : GeoDataFrame
        Census (2018) data clipped to the extenets of the city boundary.
    clipped_hazards : GeoDataFrame
        Hazard data clipped to the extents of the city boundary.
    """

    clipped_census = gpd.clip(census_data, boundary_polygon)
    clipped_hazards = []
    for hazard in hazards_list:
        clipped_hazards.append(gpd.clip(hazard, boundary_polygon))
    clipped_roads = gpd.clip(road_data, boundary_polygon)
    return clipped_census, clipped_roads, clipped_hazards
