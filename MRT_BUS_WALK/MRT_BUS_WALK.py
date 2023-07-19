import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pickle
import os
from GraphFindingAlgos import AStar_Eco
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

print("Starting")

