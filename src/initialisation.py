# -*- coding: utf-8 -*-
"""
29th of July 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 1 of the genetic algorthm. All data will be imported and pre-processed.

"""

#Import external modules
import geopandas as gpd
import pandas as pd
import rasterio as rio
import os
import numpy as np

#Import home-made modules
from src.objective_functions import *


def get_data():
    """This module gets the files from the user, and returns them opened..

    Returns
    -------
    boundaries : List of GeoDataFrames
        A list of boundaries for the urban extent and the District Plan Planning Zones.
    constraints : List of GeoDataFrames
        A list of constraints imposed by the user, which are the boundaries of the red zone and of public recreational parks
    census : GeoDataFrame
        A GeoDataFrame of the dwelling/housing 2018 census for dwellings in the Christchurch City Council region
    hazards : List of GeoDataFrames
        A list of hazards imposed upon the region, such as tsunami inundation, liquefaction vulnerability and river flooding
    coastal_flood: List of GeoDataFrames
        A list of GeoDataFrames where each new index in the list is a 10cm increase in sea level rise. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.
    distances : DataFrame
        A DataFrame of each distances (in kilometres) from each statistical area to a select amount of key activity areas.
    """

    boundary = gpd.read_file("data/boundary/urban_extent.shp")
    planning_zones = gpd.read_file("data/boundary/planning_zones.shp")
    boundaries = [boundary, planning_zones]

    tech_cats = gpd.read_file("data/raw/hazards/lique_red.shp")
    #Extract only the red zone polygons as these are the constrints
    red_zone_boundary = tech_cats.loc[tech_cats["DBH_TC"] == 'Red Zone']
    parks = gpd.read_file("data/raw/infrastructure/parks.shp")
    parks["geometry"] = parks.geometry.buffer(0) #Used to simplify the geometry as some errors occur (ring intersection)
    constraints = [red_zone_boundary, parks]

    census = gpd.read_file("data/raw/socioeconomic/census-dwellings.shp")

    distances = pd.read_csv('data/raw/socioeconomic/distances_from_SA1.csv', header=0)

    coastal_flood = []
    for slr in range(0, 310, 10):
        coastal_flood.append(gpd.read_file('data/raw/hazards/extreme_sea_level/esl_aep1_slr{}.shp'.format(slr)))

    #Enter hazards here that are not SLR coastal flood projections
    hazards = [rio.open('data/raw/hazards/tsunami.tif'), gpd.read_file("data/raw/hazards/liquefaction_vulnerability.shp"), gpd.read_file('data/raw/hazards/flood_1_in_500.shp')]

    return boundaries, constraints, census, hazards, coastal_flood, distances


def clip_to_boundary(boundary, census, hazards, coastal_flood):
    """This module clips/crops the census data and all other hazards to the urban extent boundary.

    Parameters
    ----------
    boundary : GeoDataFrame
        Boundary of the urban extent.
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region.
    hazards : List of GeoDataFrames
        A list of hazards imposed upon the region, such as tsunami inundation, liquefaction vulnerability and river flooding.
    coastal_flood : :List of GeoDataFrames
        A list of GeoDataFrames where each new index in the list is a 10cm increase in sea level rise. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.

    Returns
    -------
    clipped_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region NOT clipped to the urban extent boundary, BUT rather if it any part of the statistical area is within the boundary then it is returned.
    clipped_hazards : List of GeoDataFrames
        A list of clipped hazards imposed upon the urban extent bounary, such as tsunami inundation, liquefaction vulnerability and river flooding.
    clipped_coastal : List of GeoDataFrames
        A list of clipped GeoDataFrames where each new index in the list is a 10cm increase in sea level rise in the urban extent boundary. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.
    """

    #Extract only the relevant columns in the dwelling GeoDataFrame
    census = census[['SA12018_V1', "C18_OccP_4", 'AREA_SQ_KM', 'geometry']]

    #Generate a list of all properties that are within the boundary
    props_in = gpd.clip(census, boundary)
    props_array = props_in["SA12018_V1"].to_numpy()
    props_list = props_array.tolist()

    #Convert the census DataSet to a dictionary, where the key is the statistical area number (SA12018_V1)
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
    clipped_census.columns = pd.Index(["Dwellings", 'AREA_SQ_KM', 'geometry'])
    clipped_census.set_geometry("geometry")
    clipped_census = clipped_census.set_crs("EPSG:2193")

    #Clip the given hazards to the extend of the clipped_census.
    clipped_hazards = []
    for hazard in hazards:
        if str(type(hazard)) == "<class 'rasterio.io.DatasetReader'>":
            # We are not worried about clipping tif files, as we will assume they are a reasonable size
            clipped_hazards.append(hazard)
        elif str(type(hazard)) == "<class 'geopandas.geodataframe.GeoDataFrame'>":
            #Its a shapefile we're dealing with so geopandas is allgood.
            clipped_hazards.append(gpd.clip(hazard, clipped_census))

    #Clip the given coastla flooding data to the extend of the clipped_census.
    clipped_coastal = []
    for coastal_flooding in coastal_flood:
        clipped_coastal.append(gpd.clip(coastal_flooding, clipped_census))

    #Save all to the file structure now for safe keeping and to incerase performace speed with multiple runs of the code!
    save_clipped_to_file(clipped_census, clipped_hazards, clipped_coastal)

    return clipped_census, clipped_hazards, clipped_coastal


def save_clipped_to_file(clipped_census, clipped_hazards, clipped_coastal):
    """This module saves the clipped files to the file structre, under the "urban-optim/data/clipped" folder.

    Parameters
    ----------
    clipped_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region NOT clipped to the urban extent boundary, BUT rather if it any part of the statistical area is within the boundary then it is returned.
    clipped_hazards : List of GeoDataFrames
        A list of clipped hazards imposed upon the urban extent bounary, such as tsunami inundation, liquefaction vulnerability and river flooding.
    clipped_coastal : List of GeoDataFrames
        A list of clipped GeoDataFrames where each new index in the list is a 10cm increase in sea level rise in the urban extent boundary. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.

    Returns
    -------
    None
        No objects are returned, as this module only saves files.
    """

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
    """This module opens the clipped data if previously saved in the file structure.

    Parameters
    ----------
    hazards : List of GeoDataFrames
        A list of hazards imposed upon the region, such as tsunami inundation, liquefaction vulnerability and river flooding

    Returns
    -------
    clipped_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region NOT clipped to the urban extent boundary, BUT rather if it any part of the statistical area is within the boundary then it is returned.
    clipped_hazards : List of GeoDataFrames
        A list of clipped hazards imposed upon the urban extent bounary, such as tsunami inundation, liquefaction vulnerability and river flooding.
    clipped_coastal : List of GeoDataFrames
        A list of clipped GeoDataFrames where each new index in the list is a 10cm increase in sea level rise in the urban extent boundary. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.

    """

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


def update_constraints(constraints, planning_zones):
    """This module adds boundaries of planning zones that cannot be built on to the constraint list.

    Parameters
    ----------
    constraints : List of GeoDataFrames
        A list of constraints imposed by the user, which are the boundaries of the red zone and of public recreational parks
    planning_zones : GeoDataFrame
        Boundaries of the District Plan for the region, which details the planning zones of the region.

    Returns
    -------
    constraints : List of GeoDataFrames
        A list of constraints imposed by the user, which are the boundaries of the red zone, public recreational parks and boundaries of District Planning Zones that cannot be built on.

    """

    # This is a list of strings of all planning zones that we believe you cannot build on in the Christchurch City District
    non_building_zones_labels = ['Specific Purpose', 'Transport', 'Open Space']

    #Extract only the bad planning zones, and add/apend them to the constraints list
    non_building_zones = []
    for zone in non_building_zones_labels:
        constraints.append(planning_zones.loc[planning_zones["ZoneGroup"] == zone])

    return constraints


def apply_constraints(clipped_census, constraints):
    """This module applies the constrains given to the dwelling census data, and returns only areas that can be developed on.

    Parameters
    ----------
    clipped_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region NOT clipped to the urban extent boundary, BUT rather if it any part of the statistical area is within the boundary then it is returned.
    constraints : List of GeoDataFrames
        A list of constraints imposed by the user, which are the boundaries of the red zone, public recreational parks and boundaries of District Planning Zones that cannot be built on.

    Returns
    -------
    constrained_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent.

    """
    #Make sure the census data is in the right projection before doing the clipping
    clipped_census.to_crs("EPSG:2193")

    for constraint in constraints:
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
    clipped_census = clipped_census[~clipped_census.isna()['index']]
    constrained_census = clipped_census[clipped_census.geom_type != 'GeometryCollection']

    #Save the file for computational time and to check valitidy of the module
    constrained_census.to_file("data/processed/constrained_census.shp")
    constrained_census = gpd.read_file("data/processed/constrained_census.shp")

    return constrained_census


def add_planning_zones(constrained_census, planning_zones):
    """This module calculates what proportion of each statistical area lies within the residential, mixed use and rural Distric Plan zones.

    Parameters
    ----------
    constrained_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent.
    planning_zones : GeoDataFrame
        Boundaries of the District Plan for the region, which details the planning zones of the region.

    Returns
    -------
    zoned_census :
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone.

    """
    planning_zones = gpd.read_file("data/boundary/planning_zones.shp")
    constrained_census = gpd.read_file("data/processed/constrained_census.shp")
    constrained_census

    #Convert the census array to a dictionary so that we can add values
    census_array = constrained_census.to_numpy()
    census_dict = { census_array[i][0] : np.concatenate((census_array[i][1:], np.zeros(4))) for i in range(0, len(census_array)) }

    #List the possible District Plan Zones to be used
    possible_zones = ['Residential', 'Mixed Use', 'Rural', 'Commercial']

    for col_number in range(3, 7):
        # col_number = 4
        zone = possible_zones[col_number - 3]

        #Find the area of which is zoned by the District PLan to be residential
        res_zone = planning_zones.loc[planning_zones["ZoneGroup"] == zone]
        #Find the locations that overlap the residential zone with the census, and determine the size (area) of those polygons
        res_props = gpd.overlay(constrained_census, res_zone, how='intersection')
        areas = res_props.area
        # res_props.plot()

        for index, prop in res_props.iterrows():
            prop_number = prop[0]
            # print(census_dict[prop_number])
            property_area = 100 * float(census_dict[prop_number][1]) #in hectares
            # print("the total property area of {} is {} hectares".format(prop_number, property_area))

            #Calculate how much area has already been allocated by previous zone
            current_percentage_added = sum(census_dict[prop_number][3:])
            area_added_so_far = current_percentage_added * property_area/100
            # print("area added so far: {}".format(area_added_so_far))

            #Extract new area to add (in m^2) and what the new updated area would be in hectares
            area_to_add = float(areas[index])/10000 #in hectares
            # print("area to add: {}".format(area_to_add))

            new_area = area_to_add + area_added_so_far
            #Check if the area is less that the actual statistical area size, and adds the percentage to the right column
            if new_area <= property_area:
                census_dict[prop_number][col_number] += 100 * area_to_add/property_area
            else:
                print("DID NOT ADD NUMBER!")
                print(census_dict[prop_number])
                print("the total property area of {} is {} hectares".format(prop_number, property_area))
                print("area added so far: {}".format(area_added_so_far))
                print("area to add: {} for zone {}".format(area_to_add, zone))
                print(" ")


    #Convert the dictionry to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(census_dict, orient='index', dtype=object)
    zoned_census = gpd.GeoDataFrame(df)
    #Set some properties of the GeoDataFrame that are necessary
    zoned_census.columns = pd.Index(["Dwellings", 'AREA_SQ_KM', 'geometry', 'Res %', 'Mixed %', 'Rural %', 'Commercial %'])
    zoned_census.set_geometry("geometry")
    zoned_census = zoned_census.set_crs("EPSG:2193")

    #Save the census file to the file structure so we can validify the module works as expected
    zoned_census.to_file("data/processed/census_with_zones.shp")
    zoned_census = gpd.read_file("data/processed/census_with_zones.shp")
    zoned_census.rename(columns={'index': 'SA12018_V1'})

    return zoned_census


def add_density(zoned_census):
    """Calculated and adds the density (in dwellings per kilometre squared) to the GeoDataFrame.

    Parameters
    ----------
    zoned_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone.

    Returns
    -------
    census_dens : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone, and another column indicating density of dwellings in each statistical area.

    """

    #Change the columns from strings to floating point numbers
    zoned_census["Dwellings"] = zoned_census["Dwellings"].astype(float)
    zoned_census["AREA_SQ_KM"] = zoned_census["AREA_SQ_KM"].astype(float)

    #Add the density column, and update its value with its calculation
    zoned_census["Density"] = zoned_census["Dwellings"] / 100*zoned_census["AREA_SQ_KM"]

    #Save the census file to the file structure so we can validify the module works as expected
    zoned_census.to_file("data/processed/census_with_density.shp")
    census_dens = gpd.read_file("data/processed/census_with_density.shp")

    return census_dens


def add_f_scores(zoned_census, raw_census, clipped_hazards, clipped_coastal, distances):

    """Takes the clipped data, and amends the clipped_census data to include the f_scores for each of the objective functions in a column of the processed_census data file.

    f functions for the Christchurch optimisation study. defines the following functions:

    1. f_tsu
    2. f_cflood
    3. f_rflood
    4. f_liq
    5. f_dist
    6. f_dev

    Parameters
    ----------
    zoned_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone.
    raw_census : GeoDataFrame
        A GeoDataFrame of the dwelling/housing 2018 census for dwellings in the Christchurch City Council region
    clipped_hazards : List of GeoDataFrames
        A list of clipped hazards imposed upon the urban extent bounary, such as tsunami inundation, liquefaction vulnerability and river flooding.
    clipped_coastal : List of GeoDataFrames
        A list of clipped GeoDataFrames where each new index in the list is a 10cm increase in sea level rise in the urban extent boundary. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.
    distances : DataFrame
        A DataFrame of each distances (in kilometres) from each statistical area to a select amount of key activity areas.

    Returns
    -------
    proc_census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone, and another column indicating density of dwellings in each statistical area. 6 coloumns are also included indictaing the score of each statistical area against the 6 objective functions.

    """

    #Firstly, validate and fix all geometries of the census data set
    zoned_census["geometry"] = zoned_census.geometry.buffer(0)

    #Calculate how well each statistical area does against eahc objective function
    tsu_ratings = f_tsu(clipped_hazards[0], zoned_census)
    coastal_ratings = f_cflood(clipped_coastal, zoned_census)
    pluvial_ratings = f_rflood(clipped_hazards[2], zoned_census)
    liq_ratings = f_liq(clipped_hazards[1], zoned_census)
    distance_ratings = f_dist(distances, zoned_census)
    dev_ratings = f_dev(zoned_census)

    #Convert the census array to a dictionary so that we can add values
    census_array = zoned_census.to_numpy()
    census_list = np.ndarray.tolist(census_array)
    census_dict = { census_list[i][0] : census_list[i][1:] for i in range(0, len(census_list)) }

    #Add the f-function values to the dictionary of the parcels
    index = 0
    for key, value in census_dict.items():
        value.append(float(tsu_ratings[index]))
        value.append(float(coastal_ratings[index]))
        value.append(float(pluvial_ratings[index]))
        value.append(float(liq_ratings[index]))
        value.append(float(distance_ratings[index]))
        value.append(float(dev_ratings[index]))
        index += 1

    #Convert the merged dictionry back to a GeoDataFrame, via a Pandas DataFrame
    df = pd.DataFrame.from_dict(census_dict, orient='index', dtype=object)
    proc_census = gpd.GeoDataFrame(df)
    proc_census.columns = pd.Index(["Dwellings", 'AREA_SQ_KM', 'Res %', 'Mixed %', "Rural %", "Commercial %", "Density", "geometry", 'f_tsu', 'f_cflood', 'f_rflood', 'f_liq', 'f_dist', 'f_dev'])
    proc_census.set_geometry(col='geometry', inplace=True)

    #Save the census file to the file structure so we can validify the module works as expected
    proc_census.to_file("data/processed/census.shp")
    proc_census = gpd.read_file("data/processed/census.shp")

    return proc_census
