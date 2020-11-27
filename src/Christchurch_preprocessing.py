"""
18th of November 2020
Author: Jamie Fleming and Sam Archie

This module/script shall pre-process the christchurch raw data so it fits the format required for the main algorithm

"""

import geopandas as gpd
import os

    # miscellaneous = ["7024292", "7024296", "7026302", "7024295", "7024291", "7024284", "7024280", "7024283", "7024483", "7024484", "7024494", "7024496", "7024652", "7024703", "7026385", "7026446", "7024279", "7024347", "7024298", "7024300", "7024305", "7024348"]
    #
    # #Check each parcel to check if it is a bad one
    # good_props = []
    # for row in census["index"].items():
    #     if str(row[1]) in miscellaneous:
    #         good_props.append(False)
    #     else:
    #         good_props.append(True)
    #
    # constrained_census = census[good_props]
    #
    # census = gpd.overlay(census, constraints, how='difference', keep_geom_type=True)


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
