"""
24th of November 2020
Author: Jamie Fleming and Sam Archie

defines the objective function that can be used to normalise distances to:
 + Schools
 + Parks
 + Medical Clinics
 + Supermarkets
 + Shopping Centres

"""

# Import necessary packages
import pandas as pd
import geopandas as gpd
import numpy as np

# distance_data = pd.read_csv('data/christchurch/pre_processed/distances_from_malls.csv', header=0)
# census = gpd.read_file('data/christchurch/raw/census-dwellings.shp')

def f_dist(distance_data, census):
    """calculates the normalised distance between statistical areas and the
    nearest chosen amenity. Can be used for all 5 built in objectives

    Parameters
    ----------
    distance_data : Pandas DataFrame
        A DataFrame containing the distance to each amenity for all statistical areas
    census : GeoPandas GeoDataFrame
        Contains all the potential statistical areas (ds) to be evaluated as
        shapely polygons.

    Returns
    -------
    numpy array
        An array containing all f values in the same order as the statistical
        areas are in

    """
    census["geometry"] = census.geometry.buffer(0)

    #Collect distance to all key activity area, and store them in a dictionary
    distances_dict = {}
    for row in range(0, len(distance_data)):
        prop_number = str(distance_data['id_orig'][row])
        prev_distances_added = distances_dict.get(prop_number, [])
        updated_values = prev_distances_added + [distance_data['distance'][row]]
        distances_dict.update({prop_number : updated_values})

    #For each "good" statistical area (passed into function as census), find the min and max distances to the key activity areas
    min_distances = {}
    max_distances = []
    for prop_number in list(census['index'].unique()):
        #Get all 8 distances found previously
        all_distances = distances_dict.get(prop_number)

        #Add accordingly to the right data structure
        min_distances.update({prop_number : min(all_distances)})
        max_distances.append(max(all_distances))

    #Convert from a dictionary to to a numpy array of distances
    min_distances = np.array(list(min_distances.values()))

    #Calculate the largest distance from one statistcial area to an amenity and noralise by it!
    max_distance_observed = max(max_distances)
    f = min_distances/max_distance_observed

    return f
