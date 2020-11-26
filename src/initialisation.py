"""
25th of November 2020
Author: Jamie Fleming and Sam Archie

This module/script shall contain multiple definitions that will complete Phase 1 of the project. All data will be imported and pre-processed (constraint handling and f-scores) before being passed to the next phase.

"""

#Import external modules
import pandas as pd
import geopandas as gpd
import ruamel.yaml as yaml

### DELETE ONCE FINISHED
import sys
#This allows us to run the code from the urban-optim directory (for ease of opening and saving data) whilst looking for further code/modules in the src/fyp_code folder by adding the filepath to the system path
sys.path.insert(0, str(sys.path[0]) + '/src')
###

#Import home-made modules
from built_in_objectives import *
from user_objectives import *


def get():
    """
    Gets parameters as defined by the user in a Yaml file.
    """

    yaml_file = input('Insert Config Filename (filename.yml): ')
    if 'yml' not in yaml_file:
        yaml_file += '.yml'

    with open('config/{}'.format(yaml_file)) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        yaml_dict = yaml.safe_load(file)

    # Extract parameters
    parents = yaml_dict['parents']
    generations = yaml_dict['generations']
    p_cross = yaml_dict['crossover']
    p_mut = yaml_dict['mutation']
    p_indiv_mut = yaml_dict['individual mutation']
    weightings = yaml_dict['weightings']
    w_scheme = yaml_dict['w_scheme']
    req_dwellings = yaml_dict['req_dwellings']
    d_scheme = yaml_dict['d_scheme']
    densities = yaml_dict['densities']
    min_density = yaml_dict['min_density']
    max_density = yaml_dict['max_density']
    step_size = yaml_dict['step_size']
    scheme = w_scheme + ', ' + d_scheme

    # Extract data files
    census_fp = yaml_dict['census_fp']
    boundary_fp = yaml_dict['boundary_fp']
    constraints_fp = yaml_dict['constraints_fp']
    schools_fp = yaml_dict['schools_fp']
    parks_fp = yaml_dict['parks_fp']
    clinics_fp = yaml_dict['clinics_fp']
    supermarkets_fp = yaml_dict['supermarkets_fp']
    malls_fp = yaml_dict['malls_fp']


    return parents, generations, p_cross, p_mut, p_indiv_mut, weightings, req_dwellings, scheme, densities, min_density, max_density, step_size, census_fp, boundary_fp, constraints_fp, schools_fp, parks_fp, clinics_fp, supermarkets_fp, malls_fp


def open_data(census_fp, boundary_fp, constraints_fp, schools_fp, parks_fp, clinics_fp, supermarkets_fp, malls_fp):
    """
    Opens the data into GeoDataFrames
    """

    # City Information
    census = gpd.read_file(census_fp)
    census = census[['SA12018_V1', "C18_OccP_4", 'AREA_SQ_KM', 'geometry']]
    boundary = gpd.read_file(boundary_fp)
    constraints = gpd.read_file(constraints_fp)

    # Objectives
    obj_data = {}
    if not schools_fp == '':
        schools = gpd.read_file(schools_fp)
        schools['What'] = ['School']*len(schools)
        schools = schools[['What', 'geometry']]
        obj_data.update({'schools' : schools})
    if not parks_fp == '':
        parks = gpd.read_file(parks_fp)
        parks['What'] = ['Park']*len(parks)
        parks = parks[['What', 'geometry']]
        obj_data.update({'parks' : parks})
    if not clinics_fp == '':
        clinics = gpd.read_file(clinics_fp)
        clinics['What'] = ['Medical Clinic']*len(clinics)
        clinics = clinics[['What', 'geometry']]
        obj_data.update({'clinics' : clinics})
    if not supermarkets_fp == '':
        supermarkets = gpd.read_file(supermarkets_fp)
        supermarkets['What'] = ['Supermarket']*len(supermarkets)
        supermarkets = supermarkets[['What', 'geometry']]
        obj_data.update({'supermarkets' : supermarkets})
    if not malls_fp == '':
        malls = gpd.read_file(malls_fp)
        malls['What'] = ['Mall']*len(malls)
        malls = malls[['What', 'geometry']]
        obj_data.update({'malls' : malls})

    return census, boundary, constraints, obj_data


def clip_to_boundary(census, boundary, constraints ,obj_data):
    """

    """

    ### Constraints
    constraints['geometry'] = constraints.buffer(0)
    clipped_constraints = gpd.clip(constraints, boundary)
    clipped_constraints.to_file(r'data/christchurch/clipped/constraints.shp')

    ### Objectives
    for key in obj_data:
        clipped_key = gpd.clip(obj_data[key], boundary)
        clipped_key.to_file(r'data/christchurch/clipped/{}.shp'.format(key))
        obj_data.update({key : clipped_key})

    ### Census
    props_in = gpd.clip(census, boundary)

    #Take properties that are larger than 0.2 hectares
    props_in["area"] = props_in.area
    good_props_in = props_in.loc[props_in["area"] > 2000]

    # Create a list of property indexes
    props_array = good_props_in["SA12018_V1"].to_numpy()
    props_list = props_array.tolist()
    # len(clipped_census)
    #Convert the census DataSet to a dictionary, where the key is the statistical area number (SA12018_V1)
    census_array = good_props_in.to_numpy()
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
    df = df[[0, 1, 2]]
    clipped_census = gpd.GeoDataFrame(df)
    clipped_census.columns = pd.Index(["Dwellings", 'AREA_SQ_KM', 'geometry'])
    clipped_census.set_geometry("geometry")
    clipped_census = clipped_census.set_crs("EPSG:2193")

    clipped_census.to_file('data/christchurch/clipped/census.shp')

    return clipped_census


def open_clipped_data():
    """

    """

    clipped_census = gpd.read_file('data/christchurch/clipped/census.shp')

    clipped_constraints = gpd.read_file(r'data/christchurch/clipped/constraints.shp')


    obj_data = {}
    try:
        clipped_schools = gpd.read_file('data/christchurch/clipped/schools.shp')
        obj_data.update({'schools' : clipped_schools})
    except:
        clipped_schools = None
    try:
        clipped_parks = gpd.read_file('data/christchurch/clipped/parks.shp')
        obj_data.update({'parks' : clipped_parks})
    except:
        clipped_parks = None
    try:
        clipped_clinics = gpd.read_file('data/christchurch/clipped/clinics.shp')
        obj_data.update({'clinics' : clipped_clinics})
    except:
        clipped_clinics = None
    try:
        clipped_supermarkets = gpd.read_file('data/christchurch/clipped/supermarkets.shp')
        obj_data.update({'supermarkets' : clipped_supermarkets})
    except:
        clipped_supermarkets = None
    try:
        clipped_malls = gpd.read_file('data/christchurch/clipped/malls.shp')
        obj_data.update({'malls' : clipped_malls})
    except:
        clipped_malls = None

    return clipped_census, clipped_constraints, obj_data

parents, generations, p_cross, p_mut, p_indiv_mut, weightings, req_dwellings, scheme, densities, min_density, max_density, step_size, census_fp, boundary_fp, constraints_fp, schools_fp, parks_fp, clinics_fp, supermarkets_fp, malls_fp = get()
census, boundary, constraints, obj_data = open_data(census_fp, boundary_fp, constraints_fp, schools_fp, parks_fp, clinics_fp, supermarkets_fp, malls_fp)
clipped_census = clip_to_boundary(census, boundary, constraints ,obj_data)
clipped_census, clipped_constraints, obj_data = open_clipped_data()

clipped_census = clip_bad_SAs(clipped_census)

census = clipped_census
constraints = clipped_constraints

def apply_constraints(census, constraints):
    """

    """

    #Make sure the  data is in the right projection before doing the clipping

    from shapely.geos import TopologicalError
    #Chop the parts of the statistical areas out that are touching the constraints
    try:
        census = gpd.overlay(census, constraints, how='difference', keep_geom_type=True)
    except TopologicalError:
        print(TopologicalError)
