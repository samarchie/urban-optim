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

#Import home-made modules
import src.f_functions as func


def get_data():
    """This module gathers the data files from the user.

    Returns
    -------
    boundary
        A GeoDataFrame of the city boundary.
    roads
        A GeoDataFrame of the centre line of the road network
    census
        A GeoDataFrame of the census statistical areas of the region
    hazards
        A list of GeoDataFrames of all the hazards to use
    coastal_flood
        A list of GeoDataFrames of the coastal flooding ahzrads, where each new entry in the list is a 10cm increment of SLR

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
    road_data : GeoDataFrame
        Layer of lines of the centre-line of the road network
    census_data : GeoDataFrame
        Census (2018) data of the smallest statistical areas.
    hazards_list : List of GeoDataFrames & rasterIO Datasets
        List of all hazards to be examined.
    coastal_flood_list : List of GeoDataFrames
        List of GeoDataFrames of the coastal flooding ahzrads, where each new entry in the list is a 10cm increment of SLR

    Returns
    -------
    clipped_census : GeoDataFrame
        Census (2018) data clipped to the extents of the city boundary.
    clipped_roads : GeoDataFrame
        ayer of lines of the centre-line of the road network clipped to the extents of the city boundary
    clipped_hazards : List
        List of hazard data clipped to the extents of the city boundary.
    clipped_coastal : List
        List of coastal flooding with SLR clipped to the extents of the city boundary
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

    #Save all to the file structure now!
    save_clipped_to_file(clipped_census, clipped_roads, clipped_hazards, clipped_coastal)

    return clipped_census, clipped_roads, clipped_hazards, clipped_coastal


def save_clipped_to_file(clipped_census, clipped_roads, clipped_hazards, clipped_coastal):
    """Saves the clipped data to the file structure.

    Parameters
    ----------
    clipped_census : GeoDataFrame
        Census statistical areas in the city boundary.
    clipped_roads : GeoDataFrame
        Roads in the city boundary.
    clipped_hazards : List
        List of rasterIO Datasets and GeoDataFrames of the hazards to analyse.
    clipped_coastal : List
        List of the GeoDataFrames of the hazard from coastal inundation where each new entry in the list is a 10.

    Returns
    -------
    Returns nothing

    """

    if not os.path.exists('data/clipped'):
        os.mkdir("data/clipped")

    clipped_census.to_file("data/clipped/census-2018.shp")
    clipped_roads.to_file("data/clipped/roads.shp")

    ### ASSUME HAZARDS ARE ALREADY CLIPPED TO THE BOUNDARY. IF THEY ARE TOO LARGE THEN THE FOLLOWING CODE NEEDS TO BE UPDATED IN THE TIF SECTION AND UNCOMMENTED
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
    """If the clipped module has already run, then we need to open the data files. This will save computational time as we only need to clip the data once!

    Parameters
    ----------
    hazard_list : List
        List of the hazards, which was defined by the user in the get_data function.

    Returns
    -------
    clipped_census : GeoDataFrame
        Census (2018) data clipped to the extents of the city boundary.
    clipped_roads : GeoDataFrame
        ayer of lines of the centre-line of the road network clipped to the extents of the city boundary
    clipped_hazards : List
        List of hazard data clipped to the extents of the city boundary.
    clipped_coastal : List
        List of coastal flooding with SLR clipped to the extents of the city boundary

    """


    clipped_census = gpd.read_file("data/clipped/census-2018.shp")
    clipped_roads = gpd.read_file("data/clipped/roads.shp")

    clipped_coastal = []
    for slr in range(0, 310, 10):
        clipped_coastal.append(gpd.read_file("data/clipped/{}cm SLR.shp".format(slr)))
        clipped_hazards = []

    for hazard in hazard_list:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            clipped_hazards.append(rio.open("data/clipped/tsunami.tif"))
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            clipped_hazards.append(gpd.read_file("data/clipped/lique_red.shp"))

    return clipped_census, clipped_roads, clipped_hazards, clipped_coastal


def add_f_scores(clipped_census, raw_census, clipped_roads, clipped_hazards, clipped_coastal):
    """ Takes the clipped data, and amends the clipped_census data to include the f_scores for each of the objective functions in a column of the processed_census data file

    f functions for the Christchurch optimisation study. defines the following functions:

    1. f_tsu
    2. f_cflood
    3. f_rflood
    4. f_liq
    5. f_dist
    6. f_dev

    """

    census = clipped_census.copy()

    tsu_inundation = func.f_tsu(clipped_hazards[0], census)
    coastal_inundation = func.f_cflood(clipped_coastal, raw_census)
    ### ENTER THE OTHER F-FUNCTIONS HERE ONCE THER'RE COMPLETED!

    print(tsu_inundation)
    print(coastal_inundation)

    for index, row in census.iterrows():
        row["f_tsu"] = tsu_inundation[index]
        row["f_cflood"] = coastal_inundation[index]
        ### ENTER THE OTHER F-FUNCTIONS HERE ONCE THER'RE COMPLETED!

    print(census.head())
