# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 16:24:12 2020

@author: samwa

Tutorial notes on Geopandas and other modules I will most likely use
Basically, here is the notation and the methods I could use to solve the upcoming
problems in my spatial analysis project
"""

# Import necessary modules
import geopandas as gpd
import os
from shapely.geometry import Point, Polygon, LineString, MultiLineString, MultiPoint
from fiona.crs import from_epsg
import matplotlib.pyplot as plt
import shapely.speedups
from shapely.ops import nearest_points

# Lists folders and file in the current directory
#print(os.listdir())

# Change directory of the file path system
#os.chdir('learning_data')

# Set filepath (fix path relative to yours)
fp = r"DAMSELFISH_distributions.shp"

# Read file using gpd.read_file()
data = gpd.read_file(fp)

# Display the type of the data inputted
#print(type(data))
# Is a GeoDataFrame object

# Print first 5 rows (by default) of all the data
#print(data.head())
#print(data.tail())

# Print the column headers
# print(data.columns)

# Print specific column by splicing
#print(data['geometry'].head())

# Plot data on a map
data.plot()

# Create a output path for the data
out = r"DAMSELFISH_distributions_SELECTION.shp"

# Select first 50 rows
selection = data[0:50]

# Show what unique values are in the column selected
# print(list(data['ORIGIN'].unique()))

# Create a copy of the DataFrame with only a certain value in a specfied column
VU_people = data.loc[data['CATEGORY'] == 'VU'].copy()

# Write those rows into a new Shapefile (the default output file format is Shapefile)
selection.to_file(out)

# Iterate over selected rows and print the area for each polygon
for index, row in selection.iterrows():
    poly_area = row['geometry'].area
    #print("Polygon area at index {0} is: {1:.3f}".format(index, poly_area))

# Create a new column in the data array and input its area attribite
data['area'] = data.area

#Check that the first 2 entries in the area columns are correct
#print(data['area'].head(2))

# Maximum area
max_area = data['area'].max()

# Mean area
mean_area = data['area'].mean()

#Printting string formatting notes
#print("Max area: %s\nMean area: %s" % (round(max_area, 2), round(mean_area, 2)))

# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()

# Create a new column called 'geometry' to the GeoDataFrame
newdata['geometry'] = None

# Coordinates of the Helsinki Senate square in Decimal Degrees
coordinates = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)]

# Create a Shapely polygon from the coordinate-tuple list
poly = Polygon(coordinates)

# Insert the polygon into 'geometry' -column at index 0
newdata.loc[0, 'geometry'] = poly

# Add a new column and insert data
newdata.loc[0, 'Location'] = 'Senaatintori'

# Print coordinate system of the data
#print(newdata.crs)

# Set the GeoDataFrame's coordinate system to WGS84
newdata.crs = from_epsg(4326)

# Determine the output path for the Shapefile
outfp = r"Senaatintori.shp"

# Write the data into that Shapefile
newdata.to_file(out)

# Group the data by column 'BINOMIAL'
grouped = data.groupby('BINOMIAL')

# Iterate over the group object
for key, values in grouped:
    individual_fish = values
    
# Create a new folder called 'Results' (if does not exist) to that folder using os.makedirs() function
outFolder = ""
resultFolder = os.path.join(outFolder, 'Results')
if not os.path.exists(resultFolder):
    os.makedirs(resultFolder)
    
# Let's take a copy of our layer
data_proj = data.copy()

# Reproject the geometries by replacing the values with projected ones
data_proj = data_proj.to_crs(epsg=3035)
# Determine the CRS of the GeoDataFrame
data_proj.crs = from_epsg(3035)

# Plot the original data (WGS84)
data.plot(facecolor='gray')
# Add title
plt.title("WGS84 projection")
# Remove empty white space around the plot
plt.tight_layout()

# Plot the one with ETRS-LAEA projection
data_proj.plot(facecolor='blue')
# Add title
plt.title("ETRS Lambert Azimuthal Equal Area projection");
# Remove empty white space around the plot
plt.tight_layout()



# Create Point objects
p1 = Point(24.952242, 60.1696017)
p2 = Point(24.976567, 60.1612500)

# Create a Polygon
coords = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)]
poly = Polygon(coords)

# Check if p1 is within the polygon using the within function
p1.within(poly)
p2.within(poly)

poly.contains(p1)
poly.contains(p2)

# Find centroid of a polygon
centroid = poly.centroid

# Create two lines
line_a = LineString([(0, 0), (1, 1)])
line_b = LineString([(1, 1), (0, 2)])

# Check if lines intersect
line_a.intersects(line_b)

# Check if lines touch
line_a.touches(line_b)

# Create a MultiLineString and plot it
multi_line = MultiLineString([line_a, line_b])
#print(multi_line)

# Enabe; speedups which makes some of the spatial quieries run faster
shapely.speedups.enable()



#Notes on Spatial Joining
fp = "Vaestotietoruudukko_2015/Vaestotietoruudukko_2015.shp"
pop = gpd.read_file(fp)

# Change the name of a column
pop = pop.rename(columns={'ASUKKAITA': 'pop15'})

# Remove uneccesary columns by only keeping the ones you want
selected_cols = ['pop15', 'geometry']
pop = pop[selected_cols]

addr_fp = r"/home/geo/addresses_epsg3879.shp"
addresses = gpd.read_file(addr_fp)
# Check the coordinate refernece system is the same for both files
addresses.crs == pop.crs
# Join the files so the attribute table/Data Frane is toegtehr
join = gpd.sjoin(addresses, pop, how="inner", op="within")



# Notes on Nearest Point
orig = Point(1, 1.67)
dest1, dest2, dest3 = Point(0, 1.45), Point(2, 2), Point(0, 2.5)
destinations = MultiPoint([dest1, dest2, dest3])
nearest_geoms = nearest_points(orig, destinations)
# first item is the geometry of our origin point
near_idx0 = nearest_geoms[0]
# second item (at index 1) is the actual nearest geometry from the destination points
near_idx1 = nearest_geoms[1]
# Hence, the closest destination point seems to be the one located at coordinates (0, 1.45).

# And now finding nearest point by using two DataFrames instead
def nearest(row, geom_union, df1, df2, geom1_col='geometry', geom2_col='geometry', src_column=None):
    """Find the nearest point and return the corresponding value from specified column."""
    # Find the geometry that is closest
    nearest = df2[geom2_col] == nearest_points(row[geom1_col], geom_union)[1]
    # Get the corresponding value from df2 (matching is based on the geometry)
    value = df2[nearest][src_column].get_values()[0]
    return value

fp1 = "/home/geo/PKS_suuralue.kml"
fp2 = "/home/geo/addresses.shp"
# Allows editing and opening of KML files
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
df1 = gpd.read_file(fp1, driver='KML')
df2 = gpd.read_file(fp2)

# Create unary union from Points, which basically creates a MultiPoint object from the Point geometries.
unary_union = df2.unary_union
# Calculate the centroids for each district area.
df1['centroid'] = df1.centroid
df1['nearest_id'] = df1.apply(nearest, geom_union=unary_union, df1=df1, df2=df2, geom1_col='centroid', src_column='id', axis=1)



# Creating a custom classifier
# Let’s create a function where we classify the geometries into two classes based on a given threshold -parameter. 
#If the area of a polygon is lower than the threshold value (average size of the lake), the output column will get a value 0, if it is larger, it will get a value 1. 
def binaryClassifier(row, source_col, output_col, threshold):
    # If area of input geometry is lower that the threshold value
    if row[source_col] < threshold:
        # Update the output column with value 0
        row[output_col] = 0
    # If area of input geometry is higher than the threshold value update with value 1
    else:
        row[output_col] = 1
    # Return the updated row
    return row

# Select lakes (i.e. 'waterbodies' in the data) and make a proper copy out of our data
lakes = data.loc[data['Level3Eng'] == 'Water bodies'].copy()

lakes['small_big'] = None
lakes = lakes.apply(binaryClassifier, source_col='area_km2', output_col='small_big', threshold=l_mean_size, axis=1)
# Apply function applies the function multiple times!
lakes.plot(column='small_big', linewidth=0.05, cmap="seismic")

# A way to show how many 1'a and 0's are then in the new column:
lakes['small_big'].value_counts()



# Only include the big lakes and simplify them slightly so that they are not as detailed in the plot
#The tolerance parameter is adjusts how much geometries should be generalized. The tolerance value is tied to the coordinate system of the geometries. Thus, here the value we pass is 300 meters.
big_lakes['geom_gen'] = big_lakes.simplify(tolerance=300)




# Creating static maps
# Visualize the travel times into 9 classes using "Quantiles" classification scheme
# Add also a little bit of transparency with `alpha` parameter (ranges from 0 to 1 where 0 is fully transparent and 1 has no transparency)
my_map = grid.plot(column="car_r_t", linewidth=0.03, cmap="Reds", scheme="quantiles", k=9, alpha=0.9)

# Add roads on top of the grid
# (use ax parameter to define the map on top of which the second items are plotted)
roads.plot(ax=my_map, color="grey", linewidth=1.5)

# Add metro on top of the previous map
metro.plot(ax=my_map, color="red", linewidth=2.5)

# Remove the empty white-space around the axes
plt.tight_layout()

# Save the figure as png file with resolution of 300 dpi
outfp = r"/home/geo/data/static_map.png"
plt.savefig(outfp, dpi=300)
