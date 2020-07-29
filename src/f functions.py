"""
29th of July 2020
Author: Jamie Fleming and Sam Archie

f functions for the Christchurch optimisation study. defines the following functions:

1. f_liq
2. f_tsu
3. f_cflood
4. f_rflood
5. f_dist
6. f_dev

Data_Folder imported into each function is a string of the relative filepath to the folder where the data (hazards, amenities, etc.) is located
"""

import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import Point, Polygon

tsu_data = rasterio.open('data/raw/hazards/tsunami.tif')
census_data = gpd.read_file('data/raw/socioeconomic/2018-census-christchurch.shp')

def f_tsu(tsu_data, census_data):
    """
    Calculates the tsunami risk each parcel is prone to for a tsunami caused by a 1/2500 year earthquake in Western South America

    Development_Plan is a multipolygon, containing all the potential parcels to be evaluated as shapely polygons (mini ds)
    """

    census_data.to_crs('NZGD2000')
    centroids = []
    for geom in census_data['geometry']:
        centroids.append(geom.centroid)
    print(centroids[0])
    len(centroids)


    xs = range(tsu_data.width)
    ys = range(tsu_data.height)
