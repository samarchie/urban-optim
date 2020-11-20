"""
18th of November 2020
Author: Jamie Fleming and Sam Archie

This module/script shall contain multiple definitions that will complete Phase 1 of the project. All data will be imported and pre-processed (constraint handling and f-scores) before being passed to the next phase.

"""

#Import external modules
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
import geopandas as gpd


def get():
    """
    Creats a GUI where the input parameters for the spatial optimisation framework can be adjusted

    Returns
    -------
    NO_parents : Integer
        User specified parameter for how many parents are in a generation.
    NO_generations : Integer
        User specified parameter for hor many generations occur as part of the gentic algorithm.
    prob_crossover : Floating Point Number
        A number between 0 and 1 that represents the probability of two indiviuduals (D) within the population, swapping certian attributes (d) using a 2-point crossover technique.
    prob_mutation : Floating Point Number
        A number between 0 and 1 that represents the probability of an indiviudual (D) within the population, mutating its attributes (d) through an shuffling of attributes.
    prob_mut_indiv : Floating Point Number
        A number between 0 and 1 that represents the probability of mutating an element (d) wihtin an individual (D).
    weightings : List
        List of normalised weightings for each objective function in order.
    required_dwellings : Integer
        Number of projected dwellings required to house future residents in the urban area.
    scheme : String
        A sentence detailing the user-defined weightings and dwellings projection, in the form "weightings_name, dwellings_name"
    density_total : List of Floating Point Number
        The acceptable densities for new areas (in dwelling/hecatres) for sustainable urban development.
    min_density_Possible : Floating Point Number
        The minimum density (dwelling/hecatres) for sustainable urban development.
    max_density_Possible : Floating Point Number
        The maximum density (dwelling/hecatres) for sustainable urban development.
    when_to_plot : Generator/Range/List
        List of intergers, that represent when to halt the genetic algorithm and plot the spatial development of the current parents.
    theme : String
        Theme for the GUI windows
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
    default_city_info = {'boundary': 'P:/urban-optim/data/boundary/urban_extent.shp',
                        'census': 'P:/urban-optim/data/raw/socioeconomic/census-dwellings.shp',
                        'constraints': 'P:/urban-optim/data/raw/infrastructure/parks.shp'}
    cityinfoKeys_to_elementKeys = {'boundary': '-BOUNDARY-',
                                    'census': '-CENSUS-',
                                    'constraints': '-CONSTRAINTS-'}

    objectives_file = 'config/objectives.cfg'
    default_objectives = {'tsunami': False,
                        'coastal flooding': False,
                        'river flooding': False,
                        'liquefaction susceptibility': False,
                        'development zones': False,
                        'key activity areas': False}
    objectiveKeys_to_elementKeys = {'tsunami': '-TSU-',
                                    'coastal flooding': '-CFLOOD-',
                                    'river flooding': '-RFLOOD-',
                                    'liquefaction susceptibility': '-LIQ-',
                                    'development zones': '-DEV-',
                                    'key activity areas': '-MALL-'}

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
        if values:      # if there are stuff specified by another window, fill in those values
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

        def TextLabel(text): return sg.Text(text+':', justification='r', size=(25,1))

        layout = [  [sg.T('Objectives', font='Any 15')],
                    [sg.T('Hazards', font='Any 10')],
                    [TextLabel('Tsunami'), sg.Check('Tsunami', key='-TSU-'), sg.FileBrowse(key='-TSU-')],
                    [TextLabel('Coastal Flooding'), sg.Check('Coastal Flooding', key='-CFLOOD-'), sg.FileBrowse(key='-CFLOOD-')],
                    [TextLabel('River Flooding'), sg.Check('River Flooding', key='-RFLOOD-'), sg.FileBrowse(key='-RFLOOD-')],
                    [TextLabel('Liquefaction Susceptibility'), sg.In(key='-LIQ-'), sg.FileBrowse(key='-LIQ-')],
                    [sg.T('Urban Planning', font='Any 10')],
                    [TextLabel('Development Zones'), sg.In(key='-DEV-'), sg.FileBrowse(key='-DEV-')],
                    [sg.T('Amenities', font='Any 10')],
                    [TextLabel('Key Activity Areas (Malls)'), sg.In(key='-MALL-'), sg.FileBrowse(key='-MALL-')],

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
                  [sg.B('Change Parameters')],
                  [sg.B('Change City Data')],
                  [sg.B('Change Objectives')],
                  [sg.B('Change Settings')],
                  [sg.B('Ok')]]

        return sg.Window('Main Application', layout, margins=settings['margins'])

    ##################### Clean Up #####################
    def tidy(parameters):
        if type(parameters) == str:
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

        return parameters

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

        parameters = tidy(parameters)

        return parameters, city_info, objectives, settings

    parameters, city_info, objectives, settings = run()

    return parameters, city_info, objectives, settings

get()
