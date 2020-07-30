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
    census = gpd.read_file("data/raw/socioeconomic/2018-census-christchurch.shp")
    roads = gpd.read_file("data/raw/infrastructure/street_centre_line.shp")

    coastal_flood = []
    for slr in range(0, 310, 10):
        coastal_flood.append(gpd.read_file('data/raw/hazards/extreme_sea_level/esl_aep1_slr{}.shp'.format(slr)))

    ### Enter hazards here that are not SLR coastal flood projections
    hazards = [rio.open('data/raw/hazards/tsunami.tif'), gpd.read_file("data/raw/hazards/lique_red.shp", crs="EPSG:2193")]

    return boundary, roads, census, hazards, coastal_flood


def clip_to_boundary(boundary_polygon, road_data, census_data, hazard_list, coastal_flood_list):
    """This defination module clips all the data to the city boundary.

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
        Census (2018) data clipped to the extents of the city boundary.
    clipped_hazards : GeoDataFrame
        Hazard data clipped to the extents of the city boundary.
    """
    clipped_census = gpd.clip(census_data, boundary_polygon)
    clipped_hazards = []
    for hazard in hazard_list:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            # We are not worried about clipping tif files, as we will assume they are a reasonable size
            clipped_hazards.append(hazard)
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            #Its a shapefile we're dealing with so geopandas is allgood.
            clipped_hazards.append(gpd.clip(hazard.buffer(0), boundary_polygon))

    clipped_roads = gpd.clip(road_data, boundary_polygon)
    clipped_coastal = []
    for coastal_flooding in coastal_flood_list:
        clipped_data = gpd.clip(coastal_flooding, boundary_polygon)
        clipped_coastal.append(clipped_data)
    save_clipped_to_file(clipped_census, clipped_roads, clipped_hazards, clipped_coastal)
    return clipped_census, clipped_roads, clipped_hazards, clipped_coastal


def save_clipped_to_file(clipped_census, clipped_roads, clipped_hazards, clipped_coastal):
    """ Saves all the clipped files to the path to save computational time.
    """

    if not os.path.exists('data/clipped'):
        os.mkdir("data/clipped")

    clipped_census.to_file("data/clipped/census-2018.shp")
    clipped_roads.to_file("data/clipped/roads.shp")

### ASSUME HAZARDS ARE ALREADY CLIPPED TO THE BOUNDARY
    # for hazard in clipped_hazards:
    #     if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
    #         ### NEED TO CODE THIS PART IN ORDER TO SAVE A TIF FILE
    #
    #
    #     elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
    #         #Its a shapefile we're dealing with so geopandas is allgood.
    #         hazard.to_file("data/clipped/liq.shp")

    counter = 0
    for hazard in clipped_coastal:
        hazard.to_file("data/clipped/{}cm SLR.shp".format(counter))
        counter += 10


def open_clipped_data(hazard_list):
    """If the clipped funcation has already run before, then this module will
    reopen thepast files that have been saved.
    """
    clipped_census = gpd.read_file("data/clipped/census-2018.shp")
    clipped_roads = gpd.read_file("data/clipped/roads.shp")
    clipped_hazards = []
    clipped_coastal = []
    for slr in range(0, 310, 10):
        clipped_coastal.append(gpd.read_file("data/clipped/{}cm SLR.shp".format(slr)))
    for hazard in hazard_list:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            clipped_hazards.append(rio.open("data/clipped/tsunami.tif"))
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            clipped_hazards.append(gpd.read_file("data/clipped/lique_red.shp"))
    return clipped_census, clipped_roads, clipped_hazards, clipped_coastal
