# -*- coding: utf-8 -*-
"""
29th of July, 2020
Author: Sam Archie and Jamie Fleming

Welcome to the main function - where all the fun is!
This should be the only program that will be run, and it will import and call
upon any other functions it needs to do the genetic algorthm!

Good luck
"""

#Import our home-made modules
import src.initialise as init


def main():
    """Now this is where the magic happens!"""
    #Phase 1: initialisation
    boundary_polygon, road_data, census_data, hazards_list = init.get_data()
    clipped_census, clipped_roads, clipped_hazards = init.clip_to_boundary(boundary_polygon, road_data, census_data, hazards_list)
    clipped_census.plot()
    clipped_hazards[0].plot()


if __name__ == "__main__":
    main()
