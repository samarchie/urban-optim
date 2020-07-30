# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call
upon any other functions it needs to do the genetic algorthm!

Good luck
"""

import os
#Import our home-made modules
import src.initialise as init


def main():
    """Now this is where the magic happens!"""
    #Phase 1: initialisation
    #Get data from the user
    boundary, roads, census, hazards, coastal_flood = init.get_data()
    #Clip the data if it has not already been clipped
    ####ONCE DONE, MAKE SURE TO PUT A NOT IN THE LINE BELOW!!!!!!
    if os.path.exists("data/clipped"):
        clipped_census, clipped_roads, clipped_hazards, clipped_coastal = init.clip_to_boundary(boundary, roads, census, hazards, coastal_flood)
    else:
        clipped_census, clipped_roads, clipped_hazards, clipped_coastal = init.open_clipped_data(hazards)
    #Check to make sure we have done the right thing
    clipped_census.plot()


if __name__ == "__main__":
    main()
