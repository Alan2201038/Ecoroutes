import sys
import os
import pickle
import networkx as nx

# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from GraphFindingAlgos import AStar_Car, Dijkstra

import osmnx as ox
from geopy.geocoders import Nominatim

pfile="car_graph.pickle"

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

A=4594224456
B=244919173
latitude_A, longitude_A = graph.nodes[A]['pos']
latitude_B, longitude_B = graph.nodes[B]['pos']

print (latitude_A,longitude_A)
print(latitude_B,longitude_B)

source = (1.4293057,103.8351806)#yishun
destination = (1.3509128,103.8479885)#bishan
# Specify the source and target nodes
node_source = ox.distance.nearest_nodes(graph, source[1], source[0])
node_target = ox.distance.nearest_nodes(graph, destination[1], destination[0])

# shortest_path=nx.shortest_path(graph, node_source, node_target, weight='length')
# shortest_distance=nx.shortest_path_length(graph, node_source, node_target, weight='length')
# print(shortest_path)
# print(shortest_distance)
# ASTAR=AStar_Car.AStar(graph,node_source,node_target)
# print(ASTAR)
asd_path=Dijkstra.dijkstra(graph,node_source,node_target)
print(asd_path)