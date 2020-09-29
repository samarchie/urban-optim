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

"""

### Needed modules so far ###
import numpy as np
import rasterio as rio
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
from rasterstats import zonal_stats

# census = gpd.read_file('data/clipped/census.shp')
# census = gpd.read_file('data/processed/census_with_density.shp')
# tsunami_fp = "data/raw/hazards/tsunami.tif"
# f_tsu(tsunami_fp, census)

def f_tsu(tsunami_fp, census):
    """
    Calculates the tsunami inundation each census parcel is prone to for a
    tsunami caused by a 1/2500 year earthquake in Western South America.
    #Also accounts for 0-3 m of sea level rise, in 10 cm intervals?

    Parameters
    ----------
    tsunami_fp : string
        string of the filepath to the tsunami inundation hazard tif
    census : GeoDataFrame
        contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

    Returns
    -------
    list
        A list containing the normalised values of tsunami inundation at each
        census parcel centroid, in the same order as the census_data list

    """

    tsu_data = rio.open(tsunami_fp)

    #Convert census data to the right projection and coordinate system
    census = census.to_crs('NZGD2000')

    #Create blank arrays and fill with coordinates of all parcel centroids
    xs = []
    ys = []
    for geom in census['geometry']:
        xs.append(geom.centroid.x)
        ys.append(geom.centroid.y)

    #Put the tsunami inundation data in a readable format for centroids
    band1 = tsu_data.read(1)

    #things break if coordinates are outside the tif, so we can use this to make sure coordinates are in the tsu_data before retrieving their values
    tif_boundary = Polygon([(172.5405, -43.3568), (172.8683, -43.3568), (172.8683, -43.6863), (172.5405, -43.6863), (172.5405, -43.3568)])

    # nzgd2000 = gpd.GeoDataFrame(columns=['index'])
    # for index, row in census.iterrows():
    #     if tif_boundary.contains(row['geometry']):
    #         nzgd2000 = nzgd2000.append(row)
    #
    # nzgd2000.to_file("data/clipped/nzgd2000.shp")
    # nzgd2000 = gpd.read_file("data/clipped/nzgd2000.shp")

    #Find the (minimum, maximum, mean, median, centroid) inundation for each parcel
    inundation = []
    for index, row in census.iterrows():
        if tif_boundary.contains(row['geometry']):
            stats = zonal_stats(census['geometry'][index], tsunami_fp, stats="min max mean median")
            row, col = tsu_data.index(xs[index], ys[index])
            if row < 2792 and col < 2778:
                stats[0]['centroid'] = band1[row, col]
            else:
                stats[0]['centroid'] = 0.0

            inundation.append(stats[0]['max']) #Currently using maximum inundations from each parcel
        else:
            inundation.append(0.0)


    # inundation = []
    # for i in range(len(nzgd2000)):
    #     stats = zonal_stats(nzgd2000['geometry'][i], tsunami_fp, stats="min max mean median")
    #     row, col = tsu_data.index(xs[i], ys[i])
    #     if row < 2792 and col < 2778:
    #         stats[0]['centroid'] = band1[row, col]
    #     else:
    #         stats.append(0.0)
    #
    #     inundation.append(stats[0]['max']) #Currently using maximum inundations from each parcel

    #normalise the inundations by dividing by the maximum parcel inundation
    norm_inundation = inundation/np.max(inundation)

    return norm_inundation


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
        contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

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
        clipped_census.append(gpd.clip(census_data, flood))

    #Create a numpy array containing the sea level rise value which causes each
    #parcel to first be flooded from the coastal surge
    inundated_slr = np.full(len(census_data), None)
    for i in range(len(clipped_census)):
        flooded = clipped_census[len(clipped_census) -1 - i]['geometry'].contains(census_data['geometry'].centroid)
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


def f_rflood(pluvial_flood_data, census_data):
    """Calculates river flooding inundation

    Parameters
    ----------
    pluvial_flood_data : type
        Description of parameter `pluvial_flood_data`.
    census_data : GeoDataFrame
        contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

    Returns
    -------
    type
        Description of returned object.

    """

    #Clip the census to be only SAs affected by the flood
    clipped_census = gpd.clip(census_data, pluvial_flood_data)

    f = np.zeros(len(census_data))

    for index, row in census_data.iterrows():
        if len(clipped_census.contains(row['geometry'].centroid).unique()) > 1:
            #this checks if an SA is completely covered by the flood
            f[index] = 1
        elif len(clipped_census.intersects(row['geometry']).unique()) > 1:
            #this checks if any part of the SA is flooded. This will fail for any SA that is entirely within the flood which is why the above condition is necessary
            f[index] = 1

    return f


def f_liq(liq_data, census_data):
    """Short summary.

    Parameters
    ----------
    liquefaction_data : type
        Description of parameter `liquefaction_data`.
    census_data : GeoDataFrame
        contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

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
        if row['Liq_Cat'] == lick_cats[0]:#Liquefaction Damage is Unlikely
            lick0 = lick0.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[1]:#Very Low Liquefaction Vulnerability
            lick1 = lick1.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[2]:#Low Liquefaction Vulnerability
            lick2 = lick2.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[3]:#Liquefaction Damage is Possible
            lick3 = lick3.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[4]:#Medium Liquefaction Vulnerability
            lick4 = lick4.append({'geometry': row['geometry']}, ignore_index=True)
        elif row['Liq_Cat'] == lick_cats[5]:#High Liquefaction Vulnerability
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
                f[index] = 0.08 #damage unlikely
        index += 1

    index = 0
    for cp in in_lick1:
        for loc in cp:
            if loc:
                f[index] = 0.01 #very low vulnerability
        index += 1

    index = 0
    for cp in in_lick2:
        for loc in cp:
            if loc:
                f[index] = 0.1 #low vulnerability
        index += 1

    index = 0
    for cp in in_lick3:
        for loc in cp:
            if loc:
                f[index] = 0.9 #damage possible
        index += 1

    index = 0
    for cp in in_lick4:
        for loc in cp:
            if loc:
                f[index] = 0.5 #medium vulnerability
        index += 1

    index = 0
    for cp in in_lick5:
        for loc in cp:
            if loc:
                f[index] = 1 #high vulnerability
        index += 1

    return f


def f_dist(distance_data, census_dens):
    """calculates the normalised distance between statistical areas and the
    nearest key activity area.

    Parameters
    ----------
    distance_data : Pandas DataFrame
        A DataFrame containing the distance to each key activity area for all statistical areas
    census_dens : GeoPandas GeoDataFrame
        Contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

    Returns
    -------
    numpy array
        An array containing all f values in the same order as the statistical
        areas are in

    """
    # import pandas as pd
    # import geopandas as gpd
    # import numpy as np
    # distances = pd.read_csv('data/raw/socioeconomic/distances_from_SA1.csv', header=0)
    # census_dens = gpd.read_file("data/processed/census_with_density.shp")
    # census_dens["geometry"] = census_dens.geometry.buffer(0)

    #Collect distance to all key activity area, and store them in a dictionary
    distances_dict = {}
    for row in range(0, len(distance_data)):
        prop_number = str(distance_data['id_orig'][row])
        prev_distances_added = distances_dict.get(prop_number, [])
        updated_values = prev_distances_added + [distance_data['distance'][row]]
        distances_dict.update({prop_number : updated_values})

    #For each "good" statistical area (passed into function as census_dens), find the min and max distances to the key activity areas
    min_distances = {}
    max_distances = []
    for prop_number in list(census_dens['index'].unique()):
        #Get all 8 distances found previously
        all_distances = distances_dict.get(prop_number)

        #Add accordingly to the right data structure
        min_distances.update({prop_number : min(all_distances)})
        max_distances.append(max(all_distances))

    #Convert from a dictionary to to a numpy array of distances
    min_distances = np.array(list(min_distances.values()))

    #Calculate the largest distance from one statistcial area to a key activity area and noralise by it!
    max_distance_observed = max(max_distances)
    f = min_distances/max_distance_observed

    return f


def f_dev(census_dens):
    """Calculates the percentage of each area which is not developable, and
    returns as a decimal less than 1.

    Parameters
    ----------
    census_dens : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region of statistical areas that are not covered by a constraint and a part of the area falls within the urban extent. There are also 3 columns indicating percentage of the statistical area in each District Plan Zone, and another column indicating density of dwellings in each statistical area.

    Returns
    -------
    numpy array
        An array containing all f values in the same order as the statistical
        areas are in, indicating each statistical area's individual score against the development objective function.

    """
    f = np.zeros(len(census_dens))

    #Change the columns from strings to floating point numbers
    census_dens['Res %'] = census_dens['Res %'].astype(float)
    census_dens['Mixed %'] = census_dens['Mixed %'].astype(float)
    census_dens['Comm %'] = census_dens['Comm %'].astype(float)

    # Zhu Li, do the thing!
    for index, row in census_dens.iterrows():
        developable_score = (row['Res %'] + row['Mixed %'] + row['Comm %'])/100
        f[index] = 1 - developable_score

    return f
