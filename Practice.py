import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir(r"C:\Users\samwa\OneDrive - University of Canterbury\ENCN493 - Project")
print(["Directory List:"] + os.listdir())
os.chdir("Data")
print(os.listdir())
data = gpd.read_file("city.shp")

%matplotlib qt
data.plot()

import my name is sam 
