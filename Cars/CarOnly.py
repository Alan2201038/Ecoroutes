import sys
import os
import pickle
import networkx as nx
import math
import time
# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from GraphFindingAlgos import AStar_Car, Dijkstra
import osmnx as ox
from geopy.geocoders import Nominatim
from GUI import Map as GUI

pfile="car_graph.pickle"

def round_coordinates(coord, precision=3):
    factor = 10 ** precision
    lat = math.floor(coord[0] * factor) / factor
    lon = math.floor(coord[1] * factor) / factor
    return lat, lon

if os.path.exists(pfile):
    with open(pfile, "rb") as f:
        graph = pickle.load(f)
else:
    place_name = "Singapore"
    graph = ox.graph_from_place(place_name, network_type="drive")
    for node, data in graph.nodes(data=True):
        lon, lat = data['x'], data['y']
        graph.nodes[node]['pos'] = (lat, lon)

    with open(pfile, "wb") as f:
        pickle.dump(graph, f)

def Route(start, end):
    start_time = time.time()

    print(start)
    print(end)
    # Specify the source and target nodes
    node_source = ox.distance.nearest_nodes(graph, start[1], start[0])
    node_target = ox.distance.nearest_nodes(graph, end[1], end[0])

    ASTAR=AStar_Car.AStar(graph,node_source,node_target)
    print(ASTAR)

    geolocator = Nominatim(user_agent="ecoroutes_test")
    coordinates = []
    mode_list = []
    reduced_coordinates = []
    reduced_mode_list = []
    for node in ASTAR[0]:
        node_data = graph.nodes[node]
        latitude, longitude = node_data['y'], node_data['x']
        location = geolocator.reverse((latitude, longitude), exactly_one=True)

        # Print the location name
        # print("Location name:", location.address)
        coordinates.append((latitude, longitude))
        mode_list.append('Car')

    # Initialize variables to keep track of the previous mode and rounded coordinates
    prev_mode = None
    prev_rounded_coords = None

    for i in range(len(coordinates)):
        coord = coordinates[i]
        mode = mode_list[i]
        
        # Round the coordinates down to 3 decimal places
        rounded_coords = round_coordinates(coord)

        # Check if the rounded coordinates are the same as the previous rounded coordinates
        if rounded_coords == prev_rounded_coords:
            # Skip adding the coordinate to the reduced list
            continue

        # Add the non-walking coordinate to the reduced list
        reduced_coordinates.append(coord)
        reduced_mode_list.append(mode)
        
        # Update the previous mode and rounded coordinates
        prev_mode = mode
        prev_rounded_coords = rounded_coords
        

    # print(ASTAR)
    # print(reduced_coordinates)
    # print(reduced_mode_list)

    end_time = time.time()
    execution_time = end_time - start_time
    return (ASTAR[1], ASTAR[2], GUI.draw_map(reduced_coordinates, reduced_mode_list), execution_time)
    # asd_path=Dijkstra.dijkstra(graph,node_source,node_target)
    # print(asd_path)