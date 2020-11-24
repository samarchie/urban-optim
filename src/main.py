"""
20th of November, 2020
Author: Jamie Fleming and Sam Archie

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call upon any other functions it needs to do the genetic algorthm!

Good luck
"""

#Import all necessary modules from external sources
import os, warnings, random, sys, operator, array, math
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
import geopandas as gpd

#This all us to run the code from the urban-optim directory (for ease of opening and saving data) whilst looking for further code/modules in the src folder by adding the filepath to the system path
sys.path.insert(0, str(sys.path[0]) + '/src')

#Ignore any UserWarnings arising from mix-matched indexs when evaluating two different GeoDataFrames. Simply comment out this line if you wish death upon yourself, with ~9500 errors being printed.
warnings.simplefilter("ignore")

#Import our home-made modules
from Christchurch_preprocessing import *
from initialisation import *
# from genetic_algorithm import *
# from plotty_bois import *
from logger_config import *

#Set up the logging software to monitor progress
logger = logging.getLogger(__name__)



def main():
    """

    "whwhwhhooo, ok, here we go, focus. Code. I will Code."
    vrooooom, vroom vroom vroom vroom
    "One success, 42 errors. I eat errors for breakfast"
    ngngngngng
    "breakfast, maybe I should have had breakfast? Oh brekky could be good for me- no no no no stay focussed! Code."
    vroomvroomvroomvroomvroomvroomvroomvroom
    "I'm faster than fast, Quicker than quick. I am Lightning!"

    """

    parameters, city_info, objectives, settings = get()
    logger.info('Parameters for the algortihm are defined')

    city_data, obj_data = open_data(parameters, city_info, objectives, settings)
    user_data = open_user_data()
    logger.info('Data files for the algortihm are opened')


    if not os.path.exists('data/christchurch/clipped'):
        os.mkdir("data/christchurch/clipped")

        city_data = clip_to_boundary(city_data)
        clip_user_data(user_data, city_data)

    city_data, obj_data = open_clipped_data()
    
    logger.info('Clipping complete')
