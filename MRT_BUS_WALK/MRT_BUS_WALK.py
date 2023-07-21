import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import osmnx as ox
import matplotlib.pyplot as plt
from GraphFindingAlgos import AStar_Eco
import folium
import pickle
import os


import math
import sys
# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)


mrtGraph= "..\\Data\\MRT_Graph.pickle"
buswalkGraph="..\\Data\\Bus_Walk.pickle"
combinedGraph="..\\Data\\Combined_Graph.pickle"
WALKING_SPEED=5

def haversine(lon1, lat1, lon2, lat2):
    #Haversine used as the heuristic
    radius = 6371
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance

if os.path.exists(combinedGraph):
    with open(combinedGraph, "rb") as f:
        combined_G = pickle.load(f)

else:
    #Create combined graph if does not exist
    if os.path.exists(mrtGraph) and os.path.exists(buswalkGraph):
        with open(mrtGraph, "rb") as f:
            mrt_G = pickle.load(f)
        with open(buswalkGraph, "rb") as f:
            buswalk_G = pickle.load(f)
        combined_G = nx.compose(mrt_G, buswalk_G)

    for node in mrt_G.nodes():
        if "STATION" in node:
            # MRT NODE
            lat, lon = mrt_G.nodes[node]['pos']
            nearest_walk_bus_node = ox.distance.nearest_nodes(buswalk_G, lon, lat)

            target_node = buswalk_G.nodes[nearest_walk_bus_node]
            target_lat, target_lon = target_node['y'], target_node['x']
            dist = haversine(lon, lat, target_lon, target_lat)
            time_needed = (dist / WALKING_SPEED) * 60
            print(time_needed)
            combined_G.add_edge(node, nearest_walk_bus_node, key=f"walk_{node}_{nearest_walk_bus_node}",
                                duration=time_needed)

    with open(combinedGraph, "wb") as f:
        pickle.dump(combined_G, f)


shortest_path=AStar_Eco.AStar(combined_G,'KHATIB MRT STATION', 'BISHAN MRT STATION')
print(shortest_path)