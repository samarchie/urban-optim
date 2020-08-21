# -*- coding: utf-8 -*-
"""
29th of July 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 1 of the genetic algorthm. All data will be imported and pre-processed.

"""

#Import external modules
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
import pandas as pd
import matplotlib.pyplot as plt
import gdal
import rasterio as rio
import os
import numpy as np

#Import home-made modules
from src.objective_functions import *


def get_data():

    boundary = gpd.read_file("data/boundary/urban_extent.shp")
    planning_zones = gpd.read_file("data/boundary/planning_zones.shp")

    tech_cats = gpd.read_file("data/raw/hazards/lique_red.shp")
    red_zone_boundary = tech_cats.loc[tech_cats["DBH_TC"] == 'Red Zone']

    parks = gpd.read_file("data/raw/infrastructure/parks.shp")
    parks = parks.buffer(0)

    boundaries = [boundary, planning_zones]
    constraints = [red_zone_boundary, parks]

    census = gpd.read_file("data/raw/socioeconomic/census-dwellings.shp")

    distances = pd.read_csv('data/raw/socioeconomic/distances_from_SA1.csv', header=0)

    coastal_flood = []
    for slr in range(0, 310, 10):
        coastal_flood.append(gpd.read_file('data/raw/hazards/extreme_sea_level/esl_aep1_slr{}.shp'.format(slr)))

    ### Enter hazards here that are not SLR coastal flood projections
    hazards = [rio.open('data/raw/hazards/tsunami.tif'), gpd.read_file("data/raw/hazards/liquefaction_vulnerability.shp"), gpd.read_file('data/raw/hazards/flood_1_in_500.shp')]

    return boundaries, constraints, census, hazards, coastal_flood, distances


def clip_to_boundary(boundary, census, hazards, coastal_flood):

    #Extract only the relevant columns
    census = census[['SA12018_V1', "C18_OccP_4", 'AREA_SQ_KM', 'geometry']]

    #Generate a list of all properties that are within the boundary
    props_in = gpd.clip(census, boundary)
    props_array = props_in["SA12018_V1"].to_numpy()
    props_list = props_array.tolist()

    #Convert the census DataSet to a dictionary, via array and lists
    census_array = census.to_numpy()
    census_list = np.ndarray.tolist(census_array)
    census_dict = { census_list[i][0] : census_list[i][1:] for i in range(0, len(census_list)) }

    #For each property number in props_list, copy the census geometry data row to a new list
    new_list = []
    for number in props_list:
        values = census_dict.get(number)
        new = [number] + values
        new_list.append(new)

    #Convert that new list of the whole parcels to to a dictionary
    new_census_dict = { new_list[i][0] : new_list[i][1:] for i in range(0, len(new_list)) }

    #Convert the dictionry to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(new_census_dict, orient='index', dtype=object)
    clipped_census = gpd.GeoDataFrame(df)
    clipped_census.columns = pd.Index(["C18_OccP_4", 'AREA_SQ_KM', 'geometry'])
    clipped_census.set_geometry("geometry")
    clipped_census = clipped_census.set_crs("EPSG:2193")


    clipped_hazards = []
    for hazard in hazards:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            # We are not worried about clipping tif files, as we will assume they are a reasonable size
            clipped_hazards.append(hazard)
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            #Its a shapefile we're dealing with so geopandas is allgood.
            clipped_hazards.append(gpd.clip(hazard, clipped_census))

    clipped_coastal = []
    for coastal_flooding in coastal_flood:
        clipped_coastal.append(gpd.clip(coastal_flooding, clipped_census))

    #Save all to the file structure now!
    save_clipped_to_file(clipped_census, clipped_hazards, clipped_coastal)

    return clipped_census, clipped_hazards, clipped_coastal


def save_clipped_to_file(clipped_census, clipped_hazards, clipped_coastal):

    if not os.path.exists('data/clipped'):
        os.mkdir("data/clipped")

    clipped_census.to_file("data/clipped/census.shp")

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


def open_clipped_data(hazards):

    clipped_census = gpd.read_file("data/clipped/census.shp")

    clipped_coastal = []
    for slr in range(0, 310, 10):
        clipped_coastal.append(gpd.read_file("data/clipped/{}cm SLR.shp".format(slr)))

    clipped_hazards = []
    for hazard in hazards:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            clipped_hazards.append(hazard)
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            clipped_hazards.append(hazard)

    return clipped_census, clipped_hazards, clipped_coastal


def update_constraints(non_building_zones, constraints, planning_zones):

    non_building_zones_labels = ['Specific Purpose', 'Transport', 'Open Space']

    non_building_zones = []
    for zone in non_building_zones_labels:
        constraints.append(planning_zones.loc[planning_zones["ZoneGroup"] == zone])

    return constraints


def apply_constraints(clipped_census, constraints):
    #Take a copy of the GeoDataFrame and set its projection to NZGD2000

    clipped_census.to_crs("EPSG:2193")

    for constraint in constraints:
        print(str(type(constraint)))
        #The overlay function only take GeoDataFrames, and hence the if statements convert the constraints to the right format for overlaying
        if str(type(constraint)) == "<class 'geopandas.geoseries.GeoSeries'>":
            constraint = gpd.GeoDataFrame(constraint)
            constraint = constraint.rename(columns={0: 'geometry'})
            constraint = constraint.set_geometry('geometry')
            constraint = constraint.to_crs("EPSG:2193")

        elif str(type(constraint)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            constraint = constraint.explode()
            constraint.to_crs("EPSG:2193")

        #Chop the parts of the statistical areas out that are touching the constraint
        clipped_census = gpd.overlay(clipped_census, constraint, how='difference', keep_geom_type=False)

    #Get rid of any unnecessary empty cells (which arise from the overlaying procedure)
    constrained_census = clipped_census[~clipped_census.isna()['index']]
    constrained_census = constrained_census[constrained_census.geom_type != 'GeometryCollection']
    constrained_census.to_file("data/processed/constrained_census.shp")
    constrained_census = gpd.read_file("data/processed/constrained_census.shp")

    return constrained_census


def add_planning_zones(clipped_census, boundaries):

    boundary, planning_zones = boundaries

    #Convert the census array to a dictionary so that we can add values
    census_array = clipped_census.to_numpy()
    # census_list = np.ndarray.tolist(census_array)
    census_dict = { census_array[i][0] : np.concatenate((census_array[i][1:], np.zeros(3))) for i in range(0, len(census_array)) }

    #List the possible District Plan Zones to be used
    possible_zones = ['Residential', 'Mixed Use', 'Rural']

    for col_number in range(3, 6):
        zone = possible_zones[col_number - 3]

        #Find the area of which is zoned by the District PLan to be residential
        res_zone = planning_zones.loc[planning_zones["ZoneGroup"] == zone]

        #Find the locations that overlap the residential zone with the census
        res_props = gpd.overlay(clipped_census, res_zone, how='intersection', keep_geom_type=False)

        #Extarct the areas of each locations
        areas = res_props.area

        for index, prop in res_props.iterrows():
            prop_number = prop[0]
            #Calculate how much area has already been allocated by previous zone
            current_area_added = sum(census_dict[prop_number][3:])

            #Extract new area to add (in km^2) and what the new updated area would be
            area_to_add = float(areas[index])/float(10**6)
            new_area = area_to_add + current_area_added

            #Check if the area is less that the actual statistical area size, and adds the percentage to the right column
            if new_area <= float(census_dict[prop_number][1]):
                census_dict[prop_number][col_number] += new_area/float(census_dict[prop_number][1])

    #Convert the dictionry to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(census_dict, orient='index', dtype=object)
    zoned_census = gpd.GeoDataFrame(df)
    zoned_census
    zoned_census.columns = pd.Index(["C18_OccP_4", 'AREA_SQ_KM', 'geometry', 'Residential %', 'Mixed Use %', 'Rural %'])
    zoned_census.set_geometry("geometry")
    zoned_census = zoned_census.set_crs("EPSG:2193")

    zoned_census.to_file("data/processed/census_with_zones.shp")
    zoned_census = gpd.read_file("data/processed/census_with_zones.shp")
    zoned_census.rename(columns={'index': 'SA12018_V1'})

    return zoned_census


def add_density(census):
    """Calculated and adds the density (in dwellings per kilometre squared to the GeoDataFrame).

    Parameters
    ----------
    census : GeoDataFrame
        Census (2018) data of population and dweelings (eg merged_census).

    Returns
    -------
    census : GeoDataFrame
        The original inputted GeoDataFrame, with an extra column dedicated to the denisty calculation.

    """

    #Change the columns from strings to floating point numbers
    census["C18_OccP_4"] = census["C18_OccP_4"].astype(float)
    census["AREA_SQ_KM"] = census["AREA_SQ_KM"].astype(float)

    #Add the density column
    census["Density (dw/ha)"] = census["C18_OccP_4"] / 100*census["AREA_SQ_KM"]

    census.to_file("data/processed/census_with_density.shp")

    return census


def add_f_scores(merged_census, raw_census, clipped_hazards, clipped_coastal):
    """ Takes the clipped data, and amends the clipped_census data to include the f_scores for each of the objective functions in a column of the processed_census data file

    f functions for the Christchurch optimisation study. defines the following functions:

    1. f_tsu
    2. f_cflood
    3. f_rflood
    4. f_liq
    5. f_dist
    6. f_dev

    """
    merged_census.to_crs("EPSG:2193")

    tsu_inundation = f_tsu(clipped_hazards[0], merged_census)
    coastal_inundation = f_cflood(clipped_coastal, merged_census)
    ### ENTER THE OTHER F-FUNCTIONS HERE ONCE THER'RE COMPLETED!

    #Convert the census array to a dictionary so that we can add values
    census_array = merged_census.to_numpy()
    census_list = np.ndarray.tolist(census_array)
    census_dict = { census_list[i][0] : census_list[i][1:] for i in range(0, len(census_list)) }

    #Add the f-function values to the dictionary of the parcels
    index = 0
    for key, value in census_dict.items():
        value.append(float(tsu_inundation[index]))
        value.append(float(coastal_inundation[index]))
        ### ENTER THE OTHER F-FUNCTIONS HERE ONCE THER'RE COMPLETED!
        index += 1

    #Convert the merged dictionry back to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(census_dict, orient='index', dtype=object)
    proc_census = gpd.GeoDataFrame(df)
    print(proc_census)
    proc_census.columns = pd.Index(["C18_OccP_4", 'AREA_SQ_KM', 'Planning Zones', 'geometry', "Density (dw/ha)", 'f_tsu', 'f_cflood'])
    proc_census.set_geometry(col='geometry', inplace=True)

    #Save the processed file fo ease of computational time later on
    proc_census.to_file("data/processed/census.shp")
    proc_census = gpd.read_file("data/processed/census.shp")

    return proc_census
