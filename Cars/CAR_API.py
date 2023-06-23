import os
import pickle
import requests
import networkx as nx
from geopy.geocoders import Nominatim
import sys
sys.path.append( '../')
from GraphFindingAlgos import AStar
import math


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


pfile = "graph.pickle"

south = 1.1646
west = 103.5879
north = 1.4769
east = 104.0942

if os.path.exists(pfile):
    with open(pfile, "rb") as f:
        graph = pickle.load(f)
else:

    # Build the Overpass query string
    overpass_query = """
    [out:json];
    (
      way[highway]({south},{west},{north},{east});  // Filter by highway tag within the bounding box
    );
    out body;
    >;
    out skel qt;
    """.format(south=south, west=west, north=north, east=east)

    response = requests.get("https://overpass-api.de/api/interpreter", params={"data": overpass_query})

    data = response.json()
    graph = nx.Graph()
    #First pass to add all nodes to graph as there might be cases where the edges come before the nodes
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lon = element["lon"]
            lat = element["lat"]
            graph.add_node(node_id, pos=(lat,lon))
    for element in data["elements"]:
        if element["type"] == "way":
            node_ids = element["nodes"]
            for i in range(len(node_ids) - 1):
                node1 = node_ids[i]
                node2 = node_ids[i + 1]
                lat1,lon1 = graph.nodes[node1]['pos']
                lat2,lon2 = graph.nodes[node2]['pos']
                dist=haversine(lon1,lat1,lon2,lat2)

                graph.add_edge(node1, node2,weight=dist)

    with open(pfile, "wb") as f:
        pickle.dump(graph, f)


#Latitude,Longitude
source = (1.429464,103.835239)
destination = (1.4173,103.8330)

source_node = None
destination_node = None

for node_id, attributes in graph.nodes(data=True):
    lat,lon = attributes["pos"]
    temp1=haversine(lon, lat, source[1], source[0])
    temp2=haversine(lon, lat, destination[1], destination[0])
    if  temp1<= 0.015:
        source_node=node_id
    if  temp2<= 0.015:
        destination_node=node_id
shortest_path= AStar.AStar(graph, source_node, destination_node, destination[0], destination[1])
#shortest_path=Dijkstra.dijkstra(graph,source_node,destination_node)
print("Shortest path:", shortest_path)
geolocator = Nominatim(user_agent="ecoroutes_test")
for n in shortest_path[0]:
    node_data = graph.nodes[n]["pos"]
    latitude,longitude = node_data[0], node_data[1]
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    print("Location name:", location.address)
    print("Coordinate:",latitude,longitude)


# # Draw the graph
# plt.figure(figsize=(10, 10))
# pos = nx.get_node_attributes(graph, 'pos')
# nx.draw_networkx(graph, pos, node_size=1, node_color='black', edge_color='w', alpha=0.5, with_labels=False)
#
# # Adjust plot settings
# plt.xlim(west, east)
# plt.ylim(south, north)
# plt.axis('off')
#
# # Show the plot
# plt.show()

#TODO:Draw out route taken from shortest_path onto Map