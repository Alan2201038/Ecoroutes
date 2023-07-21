import folium
import os
import webbrowser
import csv
from io import BytesIO
import base64

# Get the directory path of the script
script_directory = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute file path to the CSV file
mrt_csv = os.path.join(script_directory,'..', 'Data', 'MRT Stations.csv')
# Construct the absolute file path to the templates folder
# map_html = os.path.join(script_directory, 'templates', 'folium.html')

# Function to search MRT Station name and change it to Lattitude and Longitude.
def find(station_name, mrt_csv):
    with open(mrt_csv, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            if row[0] == station_name:
                latitude = row[2]
                longitude = row[3]
                return float(latitude), float(longitude)

    # Return None if station name is not found
    return None, None


# This function has to take in a list of Nodes in path order OR
# a list of coordinates in path order following this format [lat, long].
# It also takes in a string 'mode' to differentiate between the modes of transport.
# The modes of transport are 'Car' and 'Train' and 'Bus'
# Afterwards, it will save the map.html file.
def draw_map(path_list, mode=None):

    # Creating a Folium Map of Singapore
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12)

    # Creating a list for path coordinates in order.
    path_coordinates = []

    # Checks the format of the path_list
    format = format_checker(path_list)

    # If the format is [ 'Station' ] format
    if format == 2:
        # Creating a for loop to get the each coordinate of the MRT Stations in path_list
        for station in path_list:
            lat, long = find(station, mrt_csv)
            path_coordinates.append([lat, long])
        #     print(station)
    elif format == 1:
        path_coordinates = path_list.copy()

    # Differentiating the modes of transport and Icons
    if mode == "Car":
        icon_map = 'car'
    elif mode == "Train":
        icon_map = 'train'
    elif mode == "Bus":
        icon_map = 'bus'
    else:
        icon_map = 'train'

    # Adding Markers into folium map
    for position in range(len(path_coordinates)):

        # Creating a special marker for the first and last station
        if position == 0:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='green', icon = icon_map , prefix='fa'),
                ).add_to(m)
        elif position == len(path_coordinates) - 1:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='red', icon = icon_map , prefix='fa'),
                ).add_to(m)
        else:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='blue', icon = icon_map, prefix='fa'),
                ).add_to(m)
            
    # Adding a line to connect the markers
    folium.PolyLine(
        locations = path_coordinates,
        dash_array = '5', 
        color = "blue", 
        weight = 2.5, 
        opacity = 1).add_to(m)
            
    # print(path_coordinates)

    # Draw Map in Folium
    # m.save(map_html)
    # webbrowser.open(map_html)
    # return map_html

    # Render m
    m.get_root().render()

    iframe = m.get_root()._repr_html_()

    return iframe



# This function checks the path list format, weather it's a list of MRT Stations or a list of coordinates.
def format_checker(path):

    if isinstance(path, list) and all(isinstance(coord, list) and len(coord) == 2 for coord in path):
        
        if all(isinstance(lat, (int, float)) and isinstance(long, (int, float)) for lat, long in path):
            return 1
        
    elif isinstance(path, list) and all(isinstance(coord, str) for coord in path):
        return 2
    
    return 0