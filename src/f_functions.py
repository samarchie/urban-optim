"""
29th of July 2020
Author: Jamie Fleming and Sam Archie

f functions for the Christchurch optimisation study. defines the following
functions:

1. f_tsu
2. f_cflood
3. f_rflood
4. f_liq
5. f_dist
6. f_dev

Data_Folder imported into each function is a string of the relative filepath to
the folder where the data (hazards, amenities, etc.) is located
"""


### Not in end code, just for testing ###
import numpy as np
import rasterio as rio
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

boundary = gpd.read_file('data/boundary/city_boundary.shp')
#tsu_data = rio.open('data/raw/hazards/tsunami.tif')
census_data = gpd.read_file('data/clipped/census-2018.shp')


#Working yay :)
def f_tsu(tsu_data, census_data):
    """
    Calculates the tsunami inundation each census parcel is prone to for a
    tsunami caused by a 1/2500 year earthquake in Western South America.
    #Also accounts for 0-3 m of sea level rise, in 10 cm intervals?

    Parameters
    ----------
    tsu_data : rasterIO Dataset
        Description of parameter `tsu_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely
        polygons.

    Returns
    -------
    list
        A list containing the normalised values of tsunami inundation at each
        census parcel centroid, in the same order as the census_data list

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

    #Find the inundation for each parcel centroid using the coordinates
    #assigned above
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

#f_tsu(tsu_data, census_data)

### Not in end code, just for testing ###
coastal_flood_data = []
for slr in range(0, 310, 10):
    coastal_flood_data.append(gpd.read_file('data/clipped/{}cm SLR.shp'.format(slr)))
###

def f_cflood(coastal_flood_data, census_data):
    """Calculates the coastal flooding inundation each census parcel is prone
    to for a 1% AEP storm surge. Also accounts for 0-3 m of sea level rise, in
    10 cm intervals

    Parameters
    ----------
    coastal_flood_data : List of GeoDataFrames
        Contains shape files of coastal inundation due to a 1% AEP storm surge
        with incremental sea level rise.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely
        polygons.
        Must have continuous indexing in GDF, no skipping

    Returns
    -------
    Numpy Array
        An array containing f values for each parcel in the order they are
        given in the census data.

    """

    #Find what parcels are affected by the coastal surge with each incremental
    #sea level rise
    clipped_census = []
    for flood in coastal_flood_data:
        clipped_census.append(gpd.clip(census_data, flood['geometry'], keep_geom_type=True))

    #Create a numpy array containing the sea level rise value which causes each
    #parcel to first be flooded from the coastal surge
    inundated_slr = np.full(len(census_data), None)
    for i in range(len(clipped_census)):
        flooded = clipped_census[len(clipped_census) -1 - i]['geometry'].contains(census_data_raw['geometry'].centroid)
        for n in range(len(flooded)):
            if flooded[n]:
                inundated_slr[n] = (30 - i)*10


    #Assign each parcel an f value based on what sea level rise causes it to
    #first be flooded from the storm surge. Use RCP2 and RCP8 as guides for
    #boundaries.
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
fcflood = f_cflood(coastal_flood_data, census_data)
fcflood

pluvial_flood_data_raw = gpd.read_file('data/raw/hazards/flood_1_in_500.shp')
pluvial_clipped = gpd.clip(pluvial_flood_data_raw, boundary)
pluvial_clipped.to_file(r'data/clipped/pluvial.shp')
pluvial_flood_data = gpd.read_file('data/clipped/pluvial.shp')
pluvial_flood_data
census_data

pd.set_option("display.max_rows", 10)
np.set_printoptions(threshold=10)

def f_rflood(pluvial_flood_data, census_data):
    """Calculates river flooding inundation

    Parameters
    ----------
    pluvial_flood_data : type
        Description of parameter `pluvial_flood_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely
        polygons.

    Returns
    -------
    type
        Description of returned object.

    """

    clipped_census = gpd.clip(census_data, pluvial_flood_data)
    clipped_census

    f = np.zeros(len(census_data))

    for index, row in census_data.iterrows():
        if len(clipped_census.contains(row['geometry'].centroid).unique()) > 1:
            f[index] = 1
        elif len(clipped_census.intersects(row['geometry']).unique()) > 1:
            f[index] = 1

    a = 0
    for bit in f:
        if bit == 1:
            a += 1
    a

    row['geometry'].centroid.within(clipped_census['geometry'])
    len(clipped_census.contains(row['geometry'].centroid).unique())
    clipped_census.intersects(row['geometry'])










#liq_data = gpd.read_file('data/raw/hazards/liquefaction_vulnerability.shp')


def f_liq(liq_data, census_data):
    """Short summary.

    Parameters
    ----------
    liquefaction_data : type
        Description of parameter `liquefaction_data`.
    census_data : GeoDataFrame
        contains all the potential parcels (ds) to be evaluated as shapely
        polygons.

    Returns
    -------
    type
        Description of returned object.

    """

    #Define the categories we want to extract
    lick_cats = ['Liquefaction Damage is Unlikely', 'Very Low Liquefaction Vulnerability', 'Low Liquefaction Vulnerability', 'Liquefaction Damage is Possible', 'Medium Liquefaction Vulnerability', 'High Liquefaction Vulnerability']

    #Create an empty GeoDataFrame of each liquefaction category, then fill with
    #polygons that make up that category from the input data
    lick0 = gpd.GeoDataFrame(columns=['geometry'])
    lick1 = gpd.GeoDataFrame(columns=['geometry'])
    lick2 = gpd.GeoDataFrame(columns=['geometry'])
    lick3 = gpd.GeoDataFrame(columns=['geometry'])
    lick4 = gpd.GeoDataFrame(columns=['geometry'])
    lick5 = gpd.GeoDataFrame(columns=['geometry'])
    for index, row in liq_data.iterrows():
        if row['Liq_Cat'] == lick_cats[0]:
            lick0 = lick0.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[1]:
            lick1 = lick1.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[2]:
            lick2 = lick2.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[3]:
            lick3 = lick3.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[4]:
            lick4 = lick4.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[5]:
            lick5 = lick5.append({'geometry': row['geometry']}, ignore_index=True)

    #Create and fill arrays of sets of boolean values. Each set will be either
    #all False or have one True, in which case the census parcel is in one of
    #the polygons defining the liquefaction zone
    in_lick0 = []
    in_lick1 = []
    in_lick2 = []
    in_lick3 = []
    in_lick4 = []
    in_lick5 = []
    for index, row in census_data.iterrows():
        in_lick0.append(lick0['geometry'].contains(row['geometry'].centroid))
        in_lick1.append(lick1['geometry'].contains(row['geometry'].centroid))
        in_lick2.append(lick2['geometry'].contains(row['geometry'].centroid))
        in_lick3.append(lick3['geometry'].contains(row['geometry'].centroid))
        in_lick4.append(lick4['geometry'].contains(row['geometry'].centroid))
        in_lick5.append(lick5['geometry'].contains(row['geometry'].centroid))

    #Create the f output array. Give a valeu based on what category each parcel
    #falls into. These values are adjustable
    f = np.zeros(len(census_data))
    index = 0 #reset to zero at each for loop
    for cp in in_lick0:
        for loc in cp:
            if loc:
                f[index] = -9 #damage unlikely
        index += 1

    index = 0
    for cp in in_lick1:
        for loc in cp:
            if loc:
                f[index] = .01 #very low vulnerability
        index += 1

    index = 0
    for cp in in_lick2:
        for loc in cp:
            if loc:
                f[index] = .1 #low vulnerability
        index += 1

    index = 0
    for cp in in_lick3:
        for loc in cp:
            if loc:
                f[index] = 9 #damage possible
        index += 1

    index = 0
    for cp in in_lick4:
        for loc in cp:
            if loc:
                f[index] = .5 #medium vulnerability
        index += 1

    index = 0
    for cp in in_lick5:
        for loc in cp:
            if loc:
                f[index] = 1 #high vulnerability
        index += 1


    return f




#def f_dist(distance_data, census_data):


#def f_dev(development_data, census_data):
