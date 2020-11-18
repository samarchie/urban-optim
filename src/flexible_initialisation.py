"""
29th of July 2020
Author: Sam Archie and Jamie Fleming

This module/script shall contain multiple definitions that will complete Phase 1 of the project. All data will be imported and pre-processed (constraint handling and f-scores) before being passed to the next phase.

"""

#Import external modules
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
from os import path

# def get_data():
#     """This module gets the files from the user, and returns them opened.
#
#     Returns
#     -------
#     boundaries : List of GeoDataFrames
#         A list of boundaries for the urban extent and the District Plan Planning Zones.
#     constraints : List of GeoDataFrames
#         A list of constraints imposed by the user, which are the boundaries of the red zone and of public recreational parks
#     census : GeoDataFrame
#         A GeoDataFrame of the dwelling/housing 2018 census for dwellings in the Christchurch City Council region
#     hazards : List of GeoDataFrames
#         A list of hazards imposed upon the region, such as tsunami inundation, liquefaction vulnerability and river flooding
#     coastal_flood: List of GeoDataFrames
#         A list of GeoDataFrames where each new index in the list is a 10cm increase in sea level rise. The GeoDataFrame indicates area inundated by the sea level rise and coastal flooding.
#     distances : DataFrame
#         A DataFrame of each distances (in kilometres) from each statistical area to a select amount of key activity areas.
#     """
#
#     # Read boundary and census files
#     event, values = sg.Window('City information data files',
#                         [[sg.T('Enter the filepath to the city boundary shapefile:')],
#                         [sg.In(key='-BOUNDARY-'), sg.FileBrowse()],
#                         [sg.T('Enter the filepath to the latest census shapefile:')],
#                         [sg.In(key='-CENSUS-'), sg.FileBrowse()],
#                         [sg.Submit()]]).read(close=True)
#     boundary = gpd.read_file(values['-BOUNDARY-'])
#     census = gpd.read_file(values['-CENSUS-'])
#
#     # Ask which built in objectives should be used, and ask for a csv file containing point coordinates
#     BI_objs = ('Distance to Shopping Centres', 'Distance to ')



###### DOCSTRING NEEDED ######
def get_parameters():
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

    settings_file = 'src/settings.cfg'
    weighting_options = ['Balanced', 'Hazard Denier', 'EQ Survivor', 'CC Enthusiast', 'Compact City']

    default_settings = {'parents': 10,
                        'generations': 10,
                        'crossover probability': 0.7,
                        'mutation probability': 0.2,
                        'individual mutation probability': 0.05,
                        'weightings': 'Balanced',
                        'required dwellings': 50000,
                        'dwelling scheme': 'high',
                        'densities': [83, 92, 111, 133],
                        'min density': 25,
                        'max density': 140,
                        'step size': 10,
                        'theme': sg.theme()}

    settingsKeys_to_elementKeys = {'parents': '-PARENTS-',
                                'generations': '-GENERATIONS-',
                                'crossover probability': '-CX_PROB-',
                                'mutation probability': '-MUT_PROB-',
                                'individual mutation probability':'-IND_MUT_PROB-',
                                'weightings': '-WEIGHTINGS-',
                                'required dwellings': '-DWELLINGS-',
                                'dwelling scheme': '-D_SCHEME-',
                                'densities': '-DENSITIES-',
                                'min density': '-MIN_DENS-',
                                'max density': '-MAX_DENS-',
                                'step size': '-STEP_SIZE-',
                                'theme': '-THEME-'}

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
        if values:      # if there are stuff specified by another window, fill in those values
            for key in settingsKeys_to_elementKeys:  # update window with the values read from settings file
                try:
                    settings[key] = values[settingsKeys_to_elementKeys[key]]
                except Exception as e:
                    print(f'Problem updating settings from window values. Key = {key}')

        with open(settings_file, 'w') as f:
            jsondump(settings, f)

        sg.popup('Settings saved')

    ##################### Make a settings window #####################
    def create_settings_window(settings, weighting_options):
        sg.theme(settings['theme'])

        def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

        layout = [  [sg.Text('Settings', font='Any 15')],
                    [TextLabel('Parents'), sg.In(key='-PARENTS-')],
                    [TextLabel('Generations'), sg.In(key='-GENERATIONS-')],
                    [TextLabel('crossover probability'), sg.In(key='-CX_PROB-')],
                    [TextLabel('mutation probability'), sg.In(key='-MUT_PROB-')],
                    [TextLabel('individual mutation probability'), sg.In(key='-IND_MUT_PROB-')],
                    [TextLabel('Weightings'), sg.Combo(weighting_options, key='-WEIGHTINGS-')    ],
                    [TextLabel('Required Dwellings'), sg.In(key='-DWELLINGS-')],
                    [TextLabel('Dwelling Scheme'), sg.In(key='-D_SCHEME-')],
                    [TextLabel('Densities'), sg.In(key='-DENSITIES-')],
                    [TextLabel('Minimum Allowable Density'), sg.In(key='-MIN_DENS-')],
                    [TextLabel('Maximum Allowable Density'), sg.In(key='-MAX_DENS-')],
                    [TextLabel('Spatial Plan Plotting Step Size'), sg.In(key='-STEP_SIZE-')],
                    [TextLabel('Theme'), sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
                    [sg.Button('Save'), sg.Button('Exit')]  ]

        window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

        for key in settingsKeys_to_elementKeys:   # update window with the values read from settings file
            try:
                window[settingsKeys_to_elementKeys[key]].update(value=settings[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

        return window

    ##################### Main Program Window #####################
    def create_main_window(settings):
        sg.theme(settings['theme'])

        layout = [[sg.T('This is my main application')],
                  [sg.T('Add your primary window stuff in here')],
                  [sg.B('Ok'), sg.B('Change Settings')]]

        return sg.Window('Main Application', layout)

    ##################### Clean Up #####################
    def tidy(settings):
        densities = []
        for bit in settings['densities'].split(','):
            if '(' in bit:
                bit = bit[1:]
            if ' ' in bit:
                bit = bit[1:]
            if ')' in bit:
                bit = bit[:-1]
            densities.append(float(bit))
        settings['densities'] = densities

        return settings

    ##################### Event Loop #####################
    def run():
        window, settings = None, load_settings(settings_file, default_settings )

        while True:             # Event Loop
            if window is None:
                window = create_main_window(settings)

            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Ok'):
                break
            if event == 'Change Settings':
                event, values = create_settings_window(settings, weighting_options).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_settings(settings_file, settings, values)
        window.close()

        settings = tidy(settings)

        return settings

    settings = run()

    scheme = settings['weightings'] + ', ' + settings['dwelling scheme']

    return int(settings['parents']), int(settings['generations']), float(settings['crossover probability']), float(settings['mutation probability']), float(settings['individual mutation probability']), settings['weightings'], int(settings['required dwellings']), scheme, settings['densities'], float(settings['min density']), float(settings['max density']), int(settings['step size']), settings['theme']

NO_parents, NO_generations, prob_crossover, prob_mutation, prob_mut_indiv, weightings, required_dwellings, scheme, density_total, min_density_possible, max_density_possible, when_to_plot, theme = get_parameters()
