"""
18th of November 2020
Author: Jamie Fleming and Sam Archie

This module/script shall pre-process the christchurch raw data so it fits the format required for the main algorithm

"""

import geopandas as gpd
import os



def pre_process_constraints():
    """
    Merge constraints into one file
    """

    ### Read data file containing red-zone polygons
    tech_cats = gpd.read_file("data/christchurch/raw/lique_red.shp")
    # Extract only the red zone polygons as these are the constraint
    red_zone_boundary = tech_cats.loc[tech_cats["DBH_TC"] == 'Red Zone']
    red_zone_boundary['What'] = 'Red Zone'
    red_zone_boundary = red_zone_boundary[['What', 'geometry']]
    constraints = red_zone_boundary

    ### Read the city planning zones
    planning_zones = gpd.read_file('data/christchurch/raw/planning_zones.shp')
    planning_zones['What'] = ['Bad Zone'] * len(planning_zones)
    planning_zones = planning_zones[['What', 'ZoneGroup', 'geometry']]
    # This is a list of strings of all planning zones that we believe you cannot build on in the Christchurch City District
    non_building_zones_labels = ['Specific Purpose', 'Transport', 'Open Space']

    for index, row in planning_zones.iterrows():
        if row['ZoneGroup'] in non_building_zones_labels:
            constraints = constraints.append(row[['What', 'geometry']])

    ### Read the parks data
    parks = gpd.read_file("data/christchurch/raw/parks.shp")
    parks["geometry"] = parks.geometry.buffer(0) #Used to simplify the geometry as some errors occur (ring intersection)
    what = ['Park'] * len(parks)
    parks['What'] = what
    constraints = constraints.append(parks[['What', 'geometry']])

    if not os.path.exists('data/christchurch/pre_processed'):
        os.mkdir("data/christchurch/pre_processed")
    constraints.to_file('data/christchurch/pre_processed/constraints.shp')


def pre_process_objective_data():
    """
    Turn polygons into points at the centroids
    """

    parks = gpd.read_file("data/christchurch/raw/parks.shp")
    parks["geometry"] = parks.geometry.buffer(0) #Used to simplify the geometry as some errors occur (ring intersection)
    parks["geometry"] = parks.geometry.centroid

    malls = gpd.read_file(r'data/christchurch/raw/key_activity_areas_updated.shp')
    malls['geometry'] = malls.geometry.buffer(0)
    malls["geometry"] = malls.geometry.centroid

    if not os.path.exists('data/christchurch/pre_processed'):
        os.mkdir("data/christchurch/pre_processed")
    parks.to_file('data/christchurch/pre_processed/parks.shp')
    malls.to_file('data/christchurch/pre_processed/malls.shp')
