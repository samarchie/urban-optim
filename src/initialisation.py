"""
18th of November 2020
Author: Jamie Fleming and Sam Archie

This module/script shall contain multiple definitions that will complete Phase 1 of the project. All data will be imported and pre-processed (constraint handling and f-scores) before being passed to the next phase.

"""

#Import external modules
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
import pandas as pd
import geopandas as gpd

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
    Creats a GUI where:
     - The input parameters for the spatial optimisation framework can be adjusted
     - File paths to the relevant data can be defined
     - Settings for PySimpleGUI windows can be adjusted

    Returns
    -------
    parameters : Dictionary
        Defines running conditions for the genetic algorithm.
        eg number of generations.
    city_info : Dictionary
        Contains file paths to data about the city.
    objectives : Dictionary
        Contains file paths to data about the planning objectives.
    settings : Dictionary
        Defines PySimpleGUI window settings.
    """

    parameters_file = 'config/parameters.cfg'
    default_parameters = {'parents': 10,
                        'generations': 10,
                        'crossover probability': 0.7,
                        'mutation probability': 0.2,
                        'individual mutation probability': 0.05,
                        'required dwellings': 50000,
                        'dwelling scheme': 'high',
                        'densities': [83, 92, 111, 133],
                        'min density': 25,
                        'max density': 140,
                        'step size': 10}
    parametersKeys_to_elementKeys = {'parents': '-PARENTS-',
                                'generations': '-GENERATIONS-',
                                'crossover probability': '-CX_PROB-',
                                'mutation probability': '-MUT_PROB-',
                                'individual mutation probability':'-IND_MUT_PROB-',
                                'required dwellings': '-DWELLINGS-',
                                'dwelling scheme': '-D_SCHEME-',
                                'densities': '-DENSITIES-',
                                'min density': '-MIN_DENS-',
                                'max density': '-MAX_DENS-',
                                'step size': '-STEP_SIZE-'}

    city_info_file = 'config/city_info.cfg'
    default_city_info = {'boundary': 'P:/urban-optim/data/christchurch/raw/urban_extent.shp',
                        'census': 'P:/urban-optim/data/christchurch/raw/census-dwellings.shp',
                        'constraints': 'P:/urban-optim/data/christchurch/pre_processed/constraints.shp'}
    cityinfoKeys_to_elementKeys = {'boundary': '-BOUNDARY-',
                                    'census': '-CENSUS-',
                                    'constraints': '-CONSTRAINTS-'}

    objectives_file = 'config/objectives.cfg'
    default_objectives = {'schools?': False,
                        'parks?': False,
                        'medical clinics?': False,
                        'supermarkets?': False,
                        'shopping centres?': False,
                        'schools': None,
                        'parks': None,
                        'medical clinics': None,
                        'supermarkets': None,
                        'shopping centres': None}
    objectiveKeys_to_elementKeys = {'schools?': '-SCHOOL?-',
                                    'parks?': '-PARK?-',
                                    'medical clinics?': '-MEDICAL?-',
                                    'supermarkets?': '-SUPER?-',
                                    'shopping centres?': '-MALL?-',
                                    'schools': '-SCHOOL-',
                                    'parks': '-PARK-',
                                    'medical clinics': '-MEDICAL-',
                                    'supermarkets': '-SUPER-',
                                    'shopping centres': '-MALL-'}

    settings_file = 'config/settings.cfg'
    default_settings = {'theme': sg.theme(),
                        'margins': [50, 50]}
    settingsKeys_to_elementKeys = {'theme': '-THEME-',
                                'margins': '-MARGINS-'}

    ########## Load/Save Parameters File ##########
    def load_parameters(parameters_file, default_parameters):
        try:
            with open(parameters_file, 'r') as f:
                parameters = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'exception {e}', 'No parameters file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
            parameters = default_parameters
            save_parameters(parameters_file, parameters, None)
        return parameters

    def save_parameters(parameters_file, parameters, values):
        if type(parameters['densities']) == str:
            densities = []
            for bit in parameters['densities'].split(','):
                if '(' in bit or '[' in bit:
                    bit = bit[1:]
                if ' ' in bit:
                    bit = bit[1:]
                if ')' in bit or ']' in bit:
                    bit = bit[:-1]
                densities.append(float(bit))
            parameters['densities'] = densities

        if values:      # if there are stuff specified by another window, fill in those values
            if type(values['-DENSITIES-']) == str:
                densities = []
                for bit in values['-DENSITIES-'].split(','):
                    if '(' in bit or '[' in bit:
                        bit = bit[1:]
                    if ' ' in bit:
                        bit = bit[1:]
                    if ')' in bit or ']' in bit:
                        bit = bit[:-1]
                    densities.append(float(bit))
                values['-DENSITIES-'] = densities

            for key in parametersKeys_to_elementKeys:  # update window with the values read from parameters file
                try:
                    parameters[key] = values[parametersKeys_to_elementKeys[key]]
                except Exception as e:
                    print(f'Problem updating parameters from window values. Key = {key}')

        with open(parameters_file, 'w') as f:
            jsondump(parameters, f)

        sg.popup('Parameters saved')

    ########## Load/Save City Information File ##########
    def load_city_info(city_info_file, default_city_info):
        try:
            with open(city_info_file, 'r') as f:
                city_info = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'exception {e}', 'No city_info file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
            city_info = default_city_info
            save_city_info(city_info_file, city_info, None)
        return city_info

    def save_city_info(city_info_file, city_info, values):
        if values:      # if there are stuff specified by another window, fill in those values
            for key in cityinfoKeys_to_elementKeys:  # update window with the values read from parameters file
                try:
                    city_info[key] = values[cityinfoKeys_to_elementKeys[key]]
                except Exception as e:
                    print(f'Problem updating city_info from window values. Key = {key}')

        with open(city_info_file, 'w') as f:
            jsondump(city_info, f)

        sg.popup('City Information saved')

    ########## Load/Save Objectives File ##########
    def load_objectives(objectives_file, default_objectives):
        try:
            with open(objectives_file, 'r') as f:
                objectives = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'exception {e}', 'No objectives file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
            objectives = default_objectives
            save_objectives(objectives_file, objectives, None)
        return objectives

    def save_objectives(objectives_file, objectives, values):
        if values:      # if there are stuff specified by another window, fill in those values
            for key in objectiveKeys_to_elementKeys:  # update window with the values read from objectives file
                try:
                    objectives[key] = values[objectiveKeys_to_elementKeys[key]]
                except Exception as e:
                    print(f'Problem updating objectives from window values. Key = {key}')

        with open(objectives_file, 'w') as f:
            jsondump(objectives, f)

        sg.popup('Objectives saved')

    ########## Load/Save Settings File ##########
    def load_settings(settings_file, default_settings):
        try:
            with open(settings_file, 'r') as f:
                settings = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
            settings = default_settings
            save_settings(settings_file, settings, None)
        return settings

    def save_settings(settings_file, settings, values):

        if type(settings['margins']) == str:
            margins = []
            for bit in settings['margins'].split(','):
                if '(' in bit or '[' in bit:
                    bit = bit[1:]
                if ' ' in bit:
                    bit = bit[1:]
                if ')' in bit or ']' in bit:
                    bit = bit[:-1]
                margins.append(float(bit))
            settings['margins'] = margins

        if values:      # if there are stuff specified by another window, fill in those values
            if type(values['-MARGINS-']) == str:
                margins = []
                if ',' in values['-MARGINS-']:
                    for bit in values['-MARGINS-'].split(','):
                        if '(' in bit or '[' in bit:
                            bit = bit[1:]
                        if ' ' in bit:
                            bit = bit[1:]
                        if ')' in bit or ']' in bit:
                            bit = bit[:-1]
                        margins.append(float(bit))
                else:
                    for bit in values['-MARGINS-'].split(' '):
                        if '(' in bit or '[' in bit:
                            bit = bit[1:]
                        if ')' in bit or ']' in bit:
                            bit = bit[:-1]
                        margins.append(float(bit))
                values['-MARGINS-'] = margins


            for key in settingsKeys_to_elementKeys:  # update window with the values read from settings file
                try:
                    settings[key] = values[settingsKeys_to_elementKeys[key]]
                except Exception as e:
                    print(f'Problem updating settings from window values. Key = {key}')

        with open(settings_file, 'w') as f:
            jsondump(settings, f)

        sg.popup('Settings saved')

    ##################### Make sub windows #####################
    def create_parameters_window(parameters, settings):
        sg.theme(settings['theme'])

        def TextLabel(text): return sg.Text(text+':', justification='r', size=(25,1))

        layout = [  [sg.Text('Parameters', font='Any 15')],
                    [TextLabel('Parents'), sg.In(key='-PARENTS-')],
                    [TextLabel('Generations'), sg.In(key='-GENERATIONS-')],
                    [TextLabel('Crossover Probability'), sg.In(key='-CX_PROB-')],
                    [TextLabel('Mutation Probability'), sg.In(key='-MUT_PROB-')],
                    [TextLabel('Individual Mutation Probability'), sg.In(key='-IND_MUT_PROB-')],
                    [TextLabel('Required Dwellings'), sg.In(key='-DWELLINGS-')],
                    [TextLabel('Dwelling Scheme'), sg.In(key='-D_SCHEME-')],
                    [TextLabel('Densities'), sg.In(key='-DENSITIES-')],
                    [TextLabel('Minimum Allowable Density'), sg.In(key='-MIN_DENS-')],
                    [TextLabel('Maximum Allowable Density'), sg.In(key='-MAX_DENS-')],
                    [TextLabel('Spatial Plan Plotting Step Size'), sg.In(key='-STEP_SIZE-')],
                    [sg.Button('Save'), sg.Button('Exit')]  ]

        window = sg.Window('Parameters', layout, margins=settings['margins'], keep_on_top=True, finalize=True)

        for key in parametersKeys_to_elementKeys:   # update window with the values read from parameters file
            try:
                window[parametersKeys_to_elementKeys[key]].update(value=parameters[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from parameters. Key = {key}')

        return window

    def create_city_info_window(city_info, settings):
        sg.theme(settings['theme'])

        def TextLabel(text): return sg.Text(text+':', justification='r', size=(25,1))

        layout = [  [sg.T('City Information', font='Any 15')],
                    [sg.T('Please enter the filepath to each shapefile', font='Any 10')],
                    [TextLabel('Boundary'), sg.In(key='-BOUNDARY-'), sg.FileBrowse(key='-BOUNDARY-')],
                    [TextLabel('Census'), sg.In(key='-CENSUS-'), sg.FileBrowse(key='-CENSUS-')],
                    [TextLabel('Constraints'), sg.In(key='-CONSTRAINTS-'), sg.FileBrowse(key='-CONSTRAINTS-')],
                    [sg.B('Save'), sg.B('Exit')]  ]

        window = sg.Window('City Information', layout, margins=settings['margins'], keep_on_top=True, finalize=True)

        for key in cityinfoKeys_to_elementKeys:   # update window with the values read from city_info file
            try:
                window[cityinfoKeys_to_elementKeys[key]].update(value=city_info[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from city_info. Key = {key}')

        return window

    def create_objectives_window(objectives, settings):
        sg.theme(settings['theme'])

        layout = [  [sg.T('Objectives', font='Any 15')],
                    [sg.T('Use built in objectives? If yes, please provide file path to the shapefile of points', font='Any 10')],
                    [sg.Check('Schools', key='-SCHOOL?-', size=(15,1)), sg.In(key='-SCHOOL-'), sg.FileBrowse(key='-SCHOOL-')],
                    [sg.Check('Parks', key='-PARK?-', size=(15,1)), sg.In(key='-PARK-'), sg.FileBrowse(key='-PARK-')],
                    [sg.Check('Medical Clinics', key='-MEDICAL?-', size=(15,1)), sg.In(key='-MEDICAL-'), sg.FileBrowse(key='-MEDICAL-')],
                    [sg.Check('Supermarkets', key='-SUPER?-', size=(15,1)), sg.In(key='-SUPER-'), sg.FileBrowse(key='-SUPER-')],
                    [sg.Check('Shopping Centres', key='-MALL?-', size=(15,1)), sg.In(key='-MALL-'), sg.FileBrowse(key='-MALL-')],

                    [sg.B('Save'), sg.B('Exit')]  ]

        window = sg.Window('Objectives', layout, margins=settings['margins'], keep_on_top=True, finalize=True)

        for key in objectiveKeys_to_elementKeys:   # update window with the values read from objectives file
            try:
                window[objectiveKeys_to_elementKeys[key]].update(value=objectives[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from objectives. Key = {key}')

        return window

    def create_settings_window(settings):
        sg.theme(settings['theme'])

        def TextLabel(text): return sg.Text(text+':', justification='r', size=(10,1))

        layout = [  [sg.Text('Settings', font='Any 15')],
                    [TextLabel('Theme'), sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
                    [TextLabel('Margins'), sg.In(key='-MARGINS-')],
                    [sg.B('Save'), sg.B('Exit')]  ]

        window = sg.Window('Settings', layout, margins=settings['margins'], keep_on_top=True, finalize=True)

        for key in settingsKeys_to_elementKeys:   # update window with the values read from parameters file
            try:
                window[settingsKeys_to_elementKeys[key]].update(value=settings[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

        return window

    ##################### Main Program Window #####################
    def create_main_window(parameters, settings):
        sg.theme(settings['theme'])

        layout = [[sg.T('This is my main application')],
                  [sg.B('Change Parameters', size=(20,1))],
                  [sg.B('Change City Data', size=(20,1))],
                  [sg.B('Change Objectives', size=(20,1))],
                  [sg.B('Change Settings', size=(20,1))],
                  [sg.B('Ok')]]

        return sg.Window('Main Application', layout, margins=settings['margins'])

    ##################### Event Loop #####################
    def run():
        window = None
        parameters = load_parameters(parameters_file, default_parameters)
        city_info = load_city_info(city_info_file, default_city_info)
        objectives = load_objectives(objectives_file, default_objectives)
        settings = load_settings(settings_file, default_settings)

        while True:             # Event Loop
            if window is None:
                window = create_main_window(parameters, settings)

            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Ok'):
                break

            if event == 'Change Parameters':
                event, values = create_parameters_window(parameters, settings).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_parameters(parameters_file, parameters, values)

            if event == 'Change City Data':
                event, values = create_city_info_window(city_info, settings).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_city_info(city_info_file, city_info, values)

            if event == 'Change Objectives':
                event, values = create_objectives_window(objectives, settings).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_objectives(objectives_file, objectives, values)

            if event == 'Change Settings':
                event, values = create_settings_window(settings).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_settings(settings_file, settings, values)
        window.close()

        return parameters, city_info, objectives, settings

    parameters, city_info, objectives, settings = run()

    return parameters, city_info, objectives, settings

parameters, city_info, objectives, settings = get()

def open_data(parameters, city_info, objectives, settings):
    """ This module opens the data into the GeoDataFrames and evaluates the .

    Parameters
    ----------
    parameters : Dictionary
        Defines running conditions for the genetic algorithm.
        eg number of generations.
    city_info : Dictionary
        Contains file paths to data about the city.
    objectives : Dictionary
        Contains file paths to data about the planning objectives.
    settings : Dictionary
        Defines PySimpleGUI window settings.

    Returns
    -------
    census : GeoDataFrame
        Dwelling/housing 2018 census for dwellings in the Christchurch City Council region NOT clipped to the urban extent boundary, BUT rather if it any part of the statistical area is within the boundary then it is returned.
    """

    # City Information
    boundary = gpd.read_file(city_info['boundary'])

    census = gpd.read_file(city_info['census'])
    census = census[['SA12018_V1', "C18_OccP_4", 'AREA_SQ_KM', 'geometry']]

    constraints = gpd.read_file(city_info['constraints'])

    city_data = {'boundary': boundary,
                'census': census,
                'constraints': constraints}

    # Objectives
    obj_data = {}
    if objectives['schools?']:
        schools = gpd.read_file(objectives['schools'])
        schools['geometry'] = [schools['geometry'][i].centroid for i in range(len(schools))]
        schools['What'] = ['School']*len(schools)
        schools = schools[['What', 'geometry']]
        obj_data.update({'schools' : schools})
    if objectives['parks?']:
        parks = gpd.read_file(objectives['parks'])
        parks['geometry'] = [parks['geometry'][i].centroid for i in range(len(parks))]
        parks['What'] = ['Park']*len(parks)
        parks = parks[['What', 'geometry']]
        obj_data.update({'parks' : parks})
    if objectives['medical clinics?']:
        medical = gpd.read_file(objectives['medical clinics'])
        medical['geometry'] = [medical['geometry'][i].centroid for i in range(len(medical))]
        medical['What'] = ['Medical Clinic']*len(medical)
        medical = medical[['What', 'geometry']]
        obj_data.update({'medical clinics' : medical})
    if objectives['supermarkets?']:
        supermarkets = gpd.read_file(objectives['supermarkets'])
        supermarkets['geometry'] = [supermarkets['geometry'][i].centroid for i in range(len(supermarkets))]
        supermarkets['What'] = ['Supermarket']*len(supermarkets)
        supermarkets = supermarkets[['What', 'geometry']]
        obj_data.update({'supermarkets' : supermarkets})
    if objectives['shopping centres?']:
        malls = gpd.read_file(objectives['shopping centres'])
        malls['geometry'] = [malls['geometry'][i].centroid for i in range(len(malls))]
        malls['What'] = ['Mall']*len(malls)
        malls = malls[['What', 'geometry']]
        obj_data.update({'malls' : malls})

    return city_data, obj_data


def clip_to_boundary(city_data):

    boundary = city_data['boundary']
    census = city_data['census']

    props_in = gpd.clip(census, boundary)

    #Take properties that are larger than 0.2 hectares
    props_in["area"] = props_in.area
    good_props_in = props_in.loc[props_in["area"] > 2000]

    # Create a list of property indexes
    props_array = good_props_in["SA12018_V1"].to_numpy()
    props_list = props_array.tolist()

    #Convert the census DataSet to a dictionary, where the key is the statistical area number (SA12018_V1)
    census_array = census.to_numpy()
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
    clipped_census = gpd.GeoDataFrame(df)
    clipped_census.columns = pd.Index(["Dwellings", 'AREA_SQ_KM', 'geometry'])
    clipped_census.set_geometry("geometry")
    clipped_census = clipped_census.set_crs("EPSG:2193")

    clipped_census.to_file('data/christchurch/clipped/clipped_census.shp')

    city_data.update({'census' : clipped_census})

    return city_data
