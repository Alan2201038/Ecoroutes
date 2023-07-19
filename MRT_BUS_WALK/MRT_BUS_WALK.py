import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import osmnx as ox
import matplotlib.pyplot as plt
import folium
import pickle
import os
mrtGraph= "..\\Data\\MRT_Pickle_Graph"
buswalkGraph="..\\Data\\Bus_Walk.pickle"

WALKING_DISTANCE=0.1
def is_close(bus_node,mrt_node):
    distance = geodesic(bus_node[1], mrt_node[1]).m
    return distance <= WALKING_DISTANCE

#HELP I DK HOW TO ADD

if os.path.exists(mrtGraph) and os.path.exists(buswalkGraph):
    with open(mrtGraph, "rb") as f:
        mrt_G = pickle.load(f)
    with open (buswalkGraph,"rb") as f:
        buswalk_G=pickle.load(f)
    combined_G=nx.compose(mrt_G,buswalk_G)

for node in buswalk_G.nodes():
    neighbors = buswalk_G.neighbors(node)
    for neigbor in neighbors:
        edge_data = buswalk_G.get_edge_data(node, neigbor)[
            0]  # Get the edge data between current_node and neighbor
        edge_weight = edge_data.get('duration', float('inf'))
        edge_transportation = edge_data.get('key', '')[:3]
        print(edge_data)