import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar, Dijkstra
from GraphFindingAlgos import AStar_CarMRT
import math
import folium
import pandas as pd
from geopy.distance import geodesic
import time
from mpl_toolkits.basemap import Basemap

start_lat = 1.4293057
start_lon = 103.8351806
end_lat = 1.3509128
end_lon = 103.8479885
amk_lat=1.3695977
amk_lon=103.849553

import networkx as nx
from math import radians, cos, sin, asin, sqrt



# Haversine formula to calculate distance between two latitude-longitude pairs
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


# Create a networkx graph
graph = nx.Graph()

# Add start and end nodes
graph.add_node("Yishun",pos=(start_lat,start_lon))
graph.add_node("Bishan", pos=(end_lat,end_lon))
graph.add_node("AMK", pos=(amk_lat,amk_lon))
# Add 10 intermediate nodes with random latitude-longitude values between Yishun to AMK (first node must be connected to Yishun, last node must be connected to AMK
intermediate_nodes = ['Node1', 'Node2', 'Node3', 'Node4', 'Node5', 'Node6', 'Node7', 'Node8', 'Node9', 'Node10']
intermediate_latitudes = [1.423 , 1.418, 1.413,  1.407, 1.404, 1.397, 1.395, 1.392, 1.388, 1.377]
intermediate_longitudes = [103.834, 103.833, 103.830,103.829, 103.827, 103.829, 103.832, 103.836,103.841, 103.847]

for i in range(len(intermediate_nodes)):
    graph.add_node(intermediate_nodes[i], pos=(intermediate_latitudes[i],intermediate_longitudes[i]))


# Calculate distances and add edges
for i in range(len(intermediate_nodes) - 1):
    node1 = intermediate_nodes[i]
    node2 = intermediate_nodes[i+1]
    distance = haversine(intermediate_latitudes[i], intermediate_longitudes[i], intermediate_latitudes[i+1], intermediate_longitudes[i+1])
    graph.add_edge(node1, node2, weight=distance)

y_distance = haversine(intermediate_latitudes[0], intermediate_longitudes[0], start_lat, start_lon)
graph.add_edge("Yishun", "Node1", weight=y_distance)
amk_distance = haversine(intermediate_latitudes[9], intermediate_longitudes[9], amk_lat, amk_lon)
graph.add_edge("Node10", "AMK", weight=amk_distance)



# Add edges for the direct connection between start and end nodes
direct_distance = haversine(start_lat, start_lon, amk_lat, amk_lon)
graph.add_edge("Yishun", "AMK", weight=15)
#graph.add_edge("Yishun", "AMK", weight=direct_distance)
graph.add_edge("AMK", "Bishan", weight=2.4)

# Print the graph information
print("Graph nodes:")
print(graph.nodes(data=True))
print("\nGraph edges:")
print(graph.edges(data=True))

map = Basemap(projection='merc', lat_0=(start_lat + end_lat) / 2, lon_0=(start_lon + end_lon) / 2,
              llcrnrlat=min(start_lat, end_lat, amk_lat, *intermediate_latitudes) - 0.02,
              llcrnrlon=min(start_lon, end_lon, amk_lon, *intermediate_longitudes) - 0.02,
              urcrnrlat=max(start_lat, end_lat, amk_lat, *intermediate_latitudes) + 0.02,
              urcrnrlon=max(start_lon, end_lon, amk_lon, *intermediate_longitudes) + 0.02)

# Draw the map
map.drawmapboundary(fill_color='black')
map.fillcontinents(color='coral', lake_color='aqua')

# Get the positions of the nodes on the map
node_positions = {}
for node in graph.nodes():
    latitude = graph.nodes[node]['pos'][0]
    longitude = graph.nodes[node]['pos'][1]
    x, y = map(longitude, latitude)
    node_positions[node] = (x, y)

def heuristic(u, v):
    # Calculate the Euclidean distance between two nodes based on their latitude and longitude
    lat1, lon1 = graph.nodes[u]['pos'][0], graph.nodes[u]['pos'][1]
    lat2, lon2 = graph.nodes[v]['pos'][0], graph.nodes[v]['pos'][1]
    return haversine(lat1, lon1, lat2, lon2)
shortest_path=AStar.AStar(graph,"Yishun","Bishan",end_lat,end_lon)
path=nx.astar_path(graph,"Yishun","Bishan",heuristic=heuristic, weight='weight')
print("Fastest path from Yishun to Bishan:")
print(path)
print("Shortest path from Yishun to Bishan:")
print(shortest_path)

# Draw the nodes
nx.draw_networkx_nodes(graph, node_positions, node_size=200, node_color='red')

# Draw the edges
nx.draw_networkx_edges(graph, node_positions, edge_color='blue')

# Add labels to the nodes
nx.draw_networkx_labels(graph, node_positions, font_color='white')

# Show the plot
plt.title("Graph Visualization")
plt.axis('off')
plt.show()


