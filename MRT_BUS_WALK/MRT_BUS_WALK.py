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

print(len(combined_G.nodes))
print(len(buswalk_G.nodes))

for node in buswalk_G.nodes():
    if isinstance(node,tuple):
        neighbors = buswalk_G.neighbors(node)
        for n in neighbors:
            print(node)
            edge_data = buswalk_G.get_edge_data(node, n)  # Get the edge data between current_node and neighbor
            key = list(edge_data.keys())[1]
            value = edge_data[key]
            des= key.split('_')[-1]
            src = key.split('_')[1]
            transportation=key.split('_')[0]
            print(transportation)
            if transportation=="bus":
                print("Works")