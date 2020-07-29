"""
29th of July 2020
Author: Jamie Fleming and Sam Archie

f functions for the Christchurch optimisation study. defines the following functions:

1. f_tsu
2. f_cflood
3. f_rflood
4. f_liq
5. f_dist
6. f_dev

Data_Folder imported into each function is a string of the relative filepath to the folder where the data (hazards, amenities, etc.) is located
"""

import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import Point, Polygon

tsu_data = rasterio.open('data/raw/hazards/tsunami.tif')
census_data = gpd.read_file('data/raw/socioeconomic/2018-census-christchurch.shp').to_crs('NZGD2000')

#Working yay :)
def f_tsu(tsu_data, census_data):
    """
    Calculates the tsunami inundation each census parcel is prone to for a tsunami caused by a 1/2500 year earthquake in Western South America.   #Also accounts for 0-3 m of sea level rise, in 10 cm intervals?

    Parameters
    ----------
    tsu_data : rasterIO Dataset
        Description of parameter `tsu_data`.
    census_data : Shapely MultiPolygon
        contains all the potential parcels (ds) to be evaluated as shapely polygons.

    Returns
    -------
    list
        A list containing the normalised values of tsunami inundation at each census parcel centroid, in the same order as the census_data list

    """

    #Create blank arrays and fill with coordinates of all parcel centroids
    xs = []
    ys = []
    for geom in nzgd2000['geometry']:
        xs.append(geom.centroid.x)
        ys.append(geom.centroid.y)

    #Put the tsunami inundation data in a readable format
    band1 = tsu_data.read(1)

    #Find the inundation for each parcel centroid using the coordinates assigned above
    inundation = []
    for i in range(len(xs)):
        row, col = tsu_data.index(xs[i], ys[i])
        if row < 2792 and col < 2792:
            inundation.append(band1[row, col])
        else:
            inundation.append(0.0)

    #normalise the inundations by dividing by the maximum parcel inundation
    norm_inundation = inundation/np.max(inundation)

    return norm_inundation



def f_cflood(coastal_flood_data, census_data):
    """Calculates the coastal flooding inundation each census parcel is prone to for a 1% AEP storm surge. Also accounts for 0-3 m of sea level rise, in 10 cm intervals

    Parameters
    ----------
    coastal_flood_data : List of GeoDataFrames
        Description of parameter `coastal_flood_data`.
    census_data : type
        Description of parameter `census_data`.

    Returns
    -------
    type
        Description of returned object.

    """
