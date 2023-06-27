import folium
import os
import webbrowser
import finder

# Get the directory path of the script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute file path to the CSV file
mrt_csv = os.path.join(script_directory,'MRTs', 'MRT Stations.csv')

# This function has to take in a list of MRT Stations in path order OR
# a list of coordinates in path order following this format [lat, long].
def draw_map(path_list):

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
            lat, long = finder.find(station, mrt_csv)
            path_coordinates.append([lat, long])
        #     print(station)
    elif format == 1:
        path_coordinates = path_list.copy()

    # Adding Markers into folium map
    for position in range(len(path_coordinates)):

        # Creating a special marker for the first and last station
        if position == 0:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='green', icon='train', prefix='fa'),
                ).add_to(m)
        elif position == len(path_coordinates) - 1:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='red', icon='train', prefix='fa'),
                ).add_to(m)
        else:
            folium.Marker(
                location = path_coordinates[position],
                popup = path_list[position],
                icon = folium.Icon(color='blue', icon='train front', prefix='fa'),
                ).add_to(m)
            
    # Adding a line to connect the markers
    folium.PolyLine(
        locations = path_coordinates,
        dash_array = '5', 
        color = "blue", 
        weight = 2.5, 
        opacity = 1).add_to(m)
            
    # print(path_coordinates)

    return m

# This function checks the path list format, weather it's a list of MRT Stations or a list of coordinates.
def format_checker(path):

    if isinstance(path, list) and all(isinstance(coord, list) and len(coord) == 2 for coord in path):
        
        if all(isinstance(lat, (int, float)) and isinstance(long, (int, float)) for lat, long in path):
            return 1
        
    elif isinstance(path, list) and all(isinstance(coord, str) for coord in path):
        return 2
    
    return 0