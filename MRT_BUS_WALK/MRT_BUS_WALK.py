import pandas as pd
import networkx as nx
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import osmnx as ox
import matplotlib.pyplot as plt
import folium
import pickle
import os
import math
import sys
# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from GraphFindingAlgos import AStar_Eco
from GUI import Map as GUI

mrtGraph= "..\\Data\\Pickle\\MRT_Graph.pickle"
buswalkGraph="..\\Data\\Pickle\\Bus_Walk.pickle"
combinedGraph="..\\Data\\Pickle\\Combined_Graph.pickle"
WALKING_SPEED=5

def round_coordinates(coord, precision=3):
    factor = 10 ** precision
    lat = math.floor(coord[0] * factor) / factor
    lon = math.floor(coord[1] * factor) / factor
    return lat, lon

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
    with open(buswalkGraph, "rb") as f:
        buswalk_G = pickle.load(f)

else:
    #Create combined graph if does not exist
    if os.path.exists(mrtGraph) and os.path.exists(buswalkGraph):
        with open(mrtGraph, "rb") as f:
            mrt_G = pickle.load(f)
        with open(buswalkGraph, "rb") as f:
            buswalk_G = pickle.load(f)
        combined_G = nx.compose(mrt_G, buswalk_G)
    print("Creating edge to the nearest bus walk node")
    for node in mrt_G.nodes():
        if "STATION" in node:
            print(node)
            # MRT NODE
            lat, lon = mrt_G.nodes[node]['pos']
            nearest_walk_bus_node = ox.distance.nearest_nodes(buswalk_G, lon, lat)
            target_node = buswalk_G.nodes[nearest_walk_bus_node]
            target_lat, target_lon = target_node['y'], target_node['x']
            dist = haversine(lon, lat, target_lon, target_lat)
            time_needed = (dist / WALKING_SPEED) * 60
            combined_G.add_edge(node, nearest_walk_bus_node, key=f"walk_{node}_{nearest_walk_bus_node}",
                                duration=time_needed)
            combined_G.add_edge(nearest_walk_bus_node,node,key=f"walk_{nearest_walk_bus_node}_{node}", duration=time_needed)
    print("Linking bus services to one another")
    bus_stops_dict = {}
    for nodes in combined_G.nodes():
        if isinstance(nodes, tuple):
            walking, busstop = nodes[:2]
            if (walking, busstop) not in bus_stops_dict:
                bus_stops_dict[(walking, busstop)] = []
                bus_stops_dict[(walking, busstop)].append(nodes)
            else:
                bus_stops_dict[(walking, busstop)].append(nodes)

    for key, values in bus_stops_dict.items():
        for i in range(len(values)):
            bus_node_A = values[i]
            for j in range(i + 1, len(values)):
                bus_node_B = values[j]
                combined_G.add_edge(bus_node_A, bus_node_B, key=f"walk_{bus_node_A}_{bus_node_B}", duration=0)
                combined_G.add_edge(bus_node_B, bus_node_A, key=f"walk_{bus_node_B}_{bus_node_A}", duration=0)

    for nodes in combined_G.nodes():
        if isinstance(nodes,tuple):
            for neighbor in combined_G.neighbors(nodes):
                if isinstance(neighbor, int):
                    edge_data = combined_G.get_edge_data(nodes, neighbor)
                    edge_key = list(edge_data.keys())[-1]
                    edge_weight = edge_data[edge_key]['duration']
                    combined_G.add_edge(neighbor, nodes, key=f"walk_{neighbor}_{nodes}", duration=edge_weight)
    with open(combinedGraph, "wb") as f:
        pickle.dump(combined_G, f)







test1=(6116490868, '46771', '904')
test2=4738663075
test3=7990780990

for neighbor in combined_G.neighbors(test1):
    if isinstance(neighbor,int):
        edge_data=combined_G.get_edge_data(test1,neighbor)
        edge_key = list(edge_data.keys())[-1]
        edge_weight = edge_data[edge_key]['duration']
        combined_G.add_edge(neighbor,test1,key=f"walk_{neighbor}_{test1}",duration=edge_weight)




#path = AStar_Eco.AStar(combined_G, (4734791178, '58341', '962B'),"YISHUN MRT STATION", mode="Eco")
path=AStar_Eco.AStar(combined_G,"YISHUN MRT STATION",(4734791178, '58341', '962B'),mode="Eco")
print(path)


# Fast=AStar_Eco.AStar(combined_G,src, des,mode="Fastest")
# Balanced=AStar_Eco.AStar(combined_G,src, des,mode="Balanced")
# Eco=AStar_Eco.AStar(combined_G,src, des)
# # print("Fastest",Fast)
# # print("Balanced",Balanced)
# print("Fastest",Fast)
# print("Balanced",Balanced)
# print("Eco",Eco)
#
# # # assuming that Eco[0] is the list of nodes in the path from source to destination
# route_nodes = Eco[0]
# # convert the nodes into Lat and Long coordinates
# route_coords = []
# for node in route_nodes:
#     point = combined_G.nodes[node]
#     if "y" in point:
#         route_coords.append([point['y'], point['x']])
#     elif "pos" in point:
#         route_coords.append([point['pos'][0],point['pos'][1]])
#
# # Create a Map centered around the start point
# m = folium.Map(location=khatib, zoom_start=14)
#
# # Add a line to the map
# folium.PolyLine(route_coords, color="red", weight=2.5, opacity=1).add_to(m)
#
# m.save("Eco.html")