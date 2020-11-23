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

    # Read data file containing red-zone polygons
    tech_cats = gpd.read_file("data/christchurch/raw/lique_red.shp")
    # Extract only the red zone polygons as these are the constraint
    red_zone_boundary = tech_cats.loc[tech_cats["DBH_TC"] == 'Red Zone']
    red_zone_boundary['What'] = 'Red Zone'
    red_zone_boundary = red_zone_boundary[['What', 'geometry']]

    # Read the parks data
    parks = gpd.read_file("data/christchurch/raw/parks.shp")
    parks["geometry"] = parks.geometry.buffer(0) #Used to simplify the geometry as some errors occur (ring intersection)
    what = ['Park'] * len(parks)
    parks['What'] = what
    constraints = parks[['What', 'geometry']]

    constraints = constraints.append(red_zone_boundary)

    if not os.path.exists('data/christchurch/pre_processed'):
        os.mkdir("data/christchurch/pre_processed")
    constraints.to_file('data/christchurch/pre_processed/constraints.shp')
