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


### Not in end code, just for testing ###
import numpy as np
import rasterio as rio
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

boundary = gpd.read_file('data/boundary/city_boundary.shp')
tsu_data = rio.open('data/raw/hazards/tsunami.tif')
census_data_raw = gpd.read_file('data/raw/socioeconomic/2018-census-christchurch.shp')
census_data = gpd.clip(census_data_raw, boundary)
###

#Working yay :)
def f_tsu(tsu_data, census_data):
    """
    Calculates the tsunami inundation each census parcel is prone to for a tsunami caused by a 1/2500 year earthquake in Western South America.   #Also accounts for 0-3 m of sea level rise, in 10 cm intervals?

    Parameters
    ----------
    tsu_data : rasterIO Dataset
        Description of parameter `tsu_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely polygons.

    Returns
    -------
    list
        A list containing the normalised values of tsunami inundation at each census parcel centroid, in the same order as the census_data list

    """

    #Convert census data to the right projection and coordinate system
    nzgd2000 = census_data.to_crs('NZGD2000')

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

f_tsu(tsu_data, census_data)

### Not in end code, just for testing ###
coastal_flood_data_raw = []
for slr in range(0, 310, 10):
    coastal_flood_data_raw.append(gpd.read_file('data/raw/hazards/extreme_sea_level/esl_aep1_slr{}.shp'.format(slr)))

coastal_flood_data = []
for slr in coastal_flood_data_raw:
    a = gpd.clip(slr, boundary)
    coastal_flood_data.append(a)

#pd.set_option("display.max_rows", 10)

import sys
#np.set_printoptions(threshold=sys.maxsize)
#np.set_printoptions(threshold=10)

###

def f_cflood(coastal_flood_data, census_data_raw):
    """Calculates the coastal flooding inundation each census parcel is prone to for a 1% AEP storm surge. Also accounts for 0-3 m of sea level rise, in 10 cm intervals

    Parameters
    ----------
    coastal_flood_data : List of GeoDataFrames
        Contains shape files of coastal inundation due to a 1% AEP storm surge with incremental sea level rise.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely polygons.
        You gotta put it in RAWWWwww "We likes it raww, and wrigglingggg"

    Returns
    -------
    Numpy Array
        An array containing f values for each parcel in the order they are given in the census data.

    """

    #Find what parcels are affected by the coastal surge with each incremental sea level rise
    clipped_census = []
    for flood in coastal_flood_data:
        clipped_census.append(gpd.clip(census_data_raw, flood['geometry'], keep_geom_type=True))

    #Create a numpy array containing the sea level rise value which causes each parcel to first be flooded from the coastal surge
    inundated_slr = np.full(len(census_data_raw), None)
    for i in range(len(clipped_census)):
        flooded = clipped_census[len(clipped_census) -1 - i]['geometry'].contains(census_data_raw['geometry'].centroid)
        for n in range(len(flooded)):
            if flooded[n]:
                inundated_slr[n] = (30 - i)*10


    #Assign each parcel an f value based on what sea level rise causes it to first be flooded from the storm surge. Use RCP2 and RCP8 as guides for boundaries.
    #f values for each range can be changed as desired
    f = np.zeros(len(inundated_slr))
    for i in range(len(inundated_slr)):
        if inundated_slr[i] == None:
            1
        elif inundated_slr[i] <= 40: #RCP2.0 lower slr prediction by 2120
            f[i] = 1
        elif inundated_slr[i] <= 60: #RCP2.0 mean slr prediction by 2120
            f[i] = 0.8
        elif inundated_slr[i] <= 100: #RCP8.0 mean slr prediction by 2120
            f[i] = 0.5
        elif inundated_slr[i] <= 130: #RCP8.0 upper slr prediction by 2120
            f[i] = 0.3
        elif inundated_slr[i] <= 300:
            f[i] = 0.1

    return f

#Ignore warnings, f list at bottom of output
fcflood = f_cflood(coastal_flood_data, census_data_raw)
fcflood

def f_rflood(pluvial_flood_data, census_data):
    """Calculates river flooding inundation

    Parameters
    ----------
    pluvial_flood_data : type
        Description of parameter `pluvial_flood_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely polygons.

    Returns
    -------
    type
        Description of returned object.

    """


### Not in final code
pd.set_option("display.max_rows", 10)
#np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(threshold=10000)


liquefaction_data_raw = gpd.read_file('data/raw/hazards/lique_red.shp')
liquefaction_data = liquefaction_data_raw.explode()
liq_data = gpd.clip(liquefaction_data.buffer(0), boundary)
liq_data
census_data.plot()

ax = census_data['geometry'].plot(zorder=0)
liq_data[0].plot(ax=ax, color='red', zorder=1)
liq_data[1].plot(ax=ax, color='green', zorder=1)
liq_data[2].plot(ax=ax, color='yellow', zorder=1)
liq_data[3].plot(ax=ax, color='orange', zorder=1)
boundary['geometry'].plot(ax=ax, color='black', alpha=0.2, zorder=2)


def f_liq(liq_data, census_data):
    """Short summary.

    Parameters
    ----------
    liquefaction_data : type
        Description of parameter `liquefaction_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely polygons.

    Returns
    -------
    type
        Description of returned object.

    """

    liq_type = np.full(len(census_data), None)

    rz_parcels = gpd.clip(census_data, liq_data[0], keep_geom_type=True)
    TC1_parcels = gpd.clip(census_data, liq_data[1], keep_geom_type=True)
    TC2_parcels = gpd.clip(census_data, liq_data[2], keep_geom_type=True)
    TC3_parcels = gpd.clip(census_data, liq_data[3], keep_geom_type=True)

    zones = np.zeros(len(census_data))

    for index, row in census_data.iterrows():
        in_rz = rz_parcels['geometry'].contains(row['geometry'].centroid)
        in_TC1 = rz_parcels['geometry'].contains(row['geometry'].centroid)
        in_TC2 = rz_parcels['geometry'].contains(row['geometry'].centroid)
        in_TC3 = rz_parcels['geometry'].contains(row['geometry'].centroid)

        if len(in_rz.unique()) > 1:
            zones[index] = 2
        elif len(in_TC1.unique()) > 1:
            zones[index] = 0.1
        elif len(in_TC2.unique()) > 1:
            zones[index] = 1
        elif len(in_TC3.unique()) > 1:
            zones[index] = 10

    zones
    #for i in in_rz:
    #    if i:
    #        print(i)




    type(rz_parcels['geometry'])


    for index, row in census_data.iterrows():
        if row['geometry'].centroid.within(rz_parcels):
            liq_type[index] = 1
        elif row['geometry'].centroid.within(TC1_parcels):
            liq_type[index] = 1
        elif row['geometry'].centroid.within(TC2_parcels):
            liq_type[index] = 1
        elif row['geometry'].centroid.within(TC3_parcels):
            liq_type[index] = 1

        #if parcel in rz_parcels:
        #    print(parcel)


    census_data
    #for poly in liquefaction_data['geometry']:
    #    type(poly)
    #    helpme = poly.contains(census_data['geometry'].centroid)
    #
    #    for n in range(len(helpme)):
    #        if helpme[n]:
    #            liq_type[n] = index
    #
    #    index += 1














def f_dist(distance_data, census_data):


def f_dev(development_data, census_data):
