# -*- coding: utf-8 -*-
"""
29th of July 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 1 of the genetic algorthm. All data will be imported and pre-processed.

"""

#Import external modules
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import pandas as pd
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
    census
        A GeoDataFrame of the census statistical areas of the region
    infra
        A list of GeoDataFrames of infrasture maps (Roads, town centres and parks)
    hazards
        A list of GeoDataFrames of all the hazards to use
    coastal_flood
        A list of GeoDataFrames of the coastal flooding ahzrads, where each new entry in the list is a 10cm increment of SLR

    """

    boundary = gpd.read_file("data/boundary/city_boundary.shp")
    census = gpd.read_file("data/raw/socioeconomic/2018-census-christchurch.shp")

    roads = gpd.read_file("data/raw/infrastructure/street_centre_line.shp")
    parks = gpd.read_file("data/raw/infrastructure/parks.shp")
    parks = parks.buffer(0)

    #Import the city/suburb centre locations from a csv file to a GeoDataFrame
    df = pd.read_csv("sam\Population center and locality labels.csv", header=0)
    town_centres = GeoDataFrame(df.drop(['x', 'y'], axis=1), crs='epsg:2193', geometry=[Point(xy) for xy in zip(df.x, df.y)])

    infra = [roads, town_centres, parks]

    coastal_flood = []
    for slr in range(0, 310, 10):
        coastal_flood.append(gpd.read_file('data/raw/hazards/extreme_sea_level/esl_aep1_slr{}.shp'.format(slr)))

    ### Enter hazards here that are not SLR coastal flood projections
    hazards = [rio.open('data/raw/hazards/tsunami.tif'), gpd.read_file("data/raw/hazards/liquefaction_vulnerability.shp")]

    return boundary, census, infra, hazards, coastal_flood


def clip_to_boundary(boundary, census, infra, hazards, coastal_flood):
    """This defination module clips all the data to the city boundary.

    Parameters
    ----------
    boundary_polygon : GeoDataFrame
        Polygon of the city boundary.
    road_data : GeoDataFrame
        Layer of lines of the centre-line of the road network
    census_data : GeoDataFrame
        Census (2018) data of the smallest statistical areas.
    hazards : List of GeoDataFrames & rasterIO Datasets
        List of all hazards to be examined.
    coastal_flood_list : List of GeoDataFrames
        List of GeoDataFrames of the coastal flooding ahzrads, where each new entry in the list is a 10cm increment of SLR
    town_centes : GeoDataFrame
        Layer of points that define the suburb/city centres

    Returns
    -------
    clipped_census : GeoDataFrame
        Census (2018) data clipped to the extents of the city boundary.
    clipped_roads : GeoDataFrame
        Layer of lines of the centre-line of the road network clipped to the extents of the city boundary
    clipped_hazards : List
        List of hazard data clipped to the extents of the city boundary.
    clipped_coastal : List
        List of coastal flooding with SLR clipped to the extents of the city boundary
    clipped_centres : GeoDataFrame
        Layer of points that define the suburb/city centres which has been clipped to the extent of the city boundary

    """

    clipped_census = gpd.clip(census, boundary)

    clipped_hazards = []
    for hazard in hazards:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            # We are not worried about clipping tif files, as we will assume they are a reasonable size
            clipped_hazards.append(hazard)
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            #Its a shapefile we're dealing with so geopandas is allgood.
            clipped_hazards.append(gpd.clip(hazard, boundary))

    clipped_infra = []
    for infrastructure in infra:
        clipped_infra.append(gpd.clip(infrastructure, boundary))

    clipped_coastal = []
    for coastal_flooding in coastal_flood:
        clipped_coastal.append(gpd.clip(coastal_flooding, boundary))


    #Save all to the file structure now!
    save_clipped_to_file(clipped_census, clipped_infra, clipped_hazards, clipped_coastal)

    return clipped_census, clipped_infra, clipped_hazards, clipped_coastal


def save_clipped_to_file(clipped_census, clipped_infra, clipped_hazards, clipped_coastal):
    """Saves the clipped data to the file structure.

    Parameters
    ----------
    clipped_census : GeoDataFrame
        Census statistical areas in the city boundary.
    clipped_infra : GeoDataFrame
        Infrastructure in the region such as roads, town centres and parks in the city boundary
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

    ### ASSUME HAZARDS ARE ALREADY CLIPPED TO THE BOUNDARY. IF THEY ARE TOO LARGE THEN THE FOLLOWING CODE NEEDS TO BE UPDATED IN THE TIF SECTION AND UNCOMMENTED
    for hazard in clipped_hazards:
        if str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            #Its a shapefile we're dealing with so geopandas is allgood.
            hazard.to_file("data/clipped/liq.shp")
        #elif str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            ### NEED TO CODE THIS PART IN ORDER TO SAVE A TIF FILE

    counter = 0
    for hazard in clipped_coastal:
        hazard.to_file("data/clipped/{}cm SLR.shp".format(counter))
        counter += 10

    clipped_infra[0].to_file("data/clipped/roads.shp")
    clipped_infra[1].to_file("data/clipped/town_centres.shp")
    clipped_infra[2].to_file("data/clipped/parks.shp")


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

    clipped_infra = []
    clipped_infra.append(gpd.read_file("data/clipped/roads.shp"))
    clipped_infra.append(gpd.read_file("data/clipped/town_centres.shp"))
    clipped_infra.append(gpd.read_file("data/clipped/parks.shp"))

    clipped_coastal = []
    for slr in range(0, 310, 10):
        clipped_coastal.append(gpd.read_file("data/clipped/{}cm SLR.shp".format(slr)))

    clipped_hazards = []
    for hazard in hazard_list:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            clipped_hazards.append(rio.open("data/clipped/tsunami.tif"))
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            clipped_hazards.append(gpd.read_file("data/clipped/liq.shp"))

    return clipped_census, clipped_infra, clipped_hazards, clipped_coastal


def add_f_scores(clipped_census, raw_census, clipped_infra, clipped_hazards, clipped_coastal):
    """ Takes the clipped data, and amends the clipped_census data to include the f_scores for each of the objective functions in a column of the processed_census data file

    f functions for the Christchurch optimisation study. defines the following functions:

    1. f_tsu
    2. f_cflood
    3. f_rflood
    4. f_liq
    5. f_dist
    6. f_dev

    """

    census = clipped_census[['SA12018_V1', 'C06_CURPop', 'C13_CURPop', 'C18_CURPop', 'C06_CNPop', 'C13_CNPop', 'C18_CNPop', 'LANDWATER', 'LANDWATER_', 'LAND_AREA_', 'AREA_SQ_KM', 'SHAPE_Leng', 'geometry']]
    census = gpd.read_file("data/raw/ss/censusnew.shp")
    tsu_inundation = func.f_tsu(clipped_hazards[0], census)
    coastal_inundation = func.f_cflood(clipped_coastal, raw_census)
    ### ENTER THE OTHER F-FUNCTIONS HERE ONCE THER'RE COMPLETED!

    census_array = census.to_numpy()
    census_list = np.ndarray.tolist(census_array)
    index = 0

    for row in census_list:
        row.append(tsu_inundation[index])
        row.append(coastal_inundation[index])

    census_array = np.array(census_list,dtype=object)
    census_frame = gpd.GeoDataFrame(census_array)
    census_frame.columns = census.keys().append(pd.Index(['f_tsu', 'f_cflood']))
    print(census_frame.head())


    #proc_census_array[index] = np.append(census_array, coastal_inundation[index])

    # proc_census = gpd.GeoDataFrame(proc_census_array)
    # proc_census.columns = census.keys()
    # print(census_array[0])
    # print(proc_census.head())
    # print(proc_census.keys())
