import os
import pickle
import requests
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar_Eco,AStar_Single
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
    graph = nx.DiGraph()
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
            if "oneway" in element["tags"]:
                oneway = element["tags"]["oneway"]
                if oneway == "yes":
                    # Add oneway connection into graph to account for oneway streets
                    for i in range(len(node_ids) - 1):
                        node1 = node_ids[i]
                        node2 = node_ids[i + 1]
                        lat1, lon1 = graph.nodes[node1]['pos']
                        lat2, lon2 = graph.nodes[node2]['pos']
                        dist = haversine(lon1, lat1, lon2, lat2)

                        graph.add_edge(node1, node2, weight=dist)
                else:
                    for i in range(len(node_ids) - 1):
                        node1 = node_ids[i]
                        node2 = node_ids[i + 1]
                        lat1, lon1 = graph.nodes[node1]['pos']
                        lat2, lon2 = graph.nodes[node2]['pos']
                        dist = haversine(lon1, lat1, lon2, lat2)

                        graph.add_edge(node1, node2, weight=dist)
                        graph.add_edge(node2, node1, weight=dist)
            else:
                # Add bidirectional edge
                for i in range(len(node_ids) - 1):
                    node1 = node_ids[i]
                    node2 = node_ids[i + 1]
                    lat1, lon1 = graph.nodes[node1]['pos']
                    lat2, lon2 = graph.nodes[node2]['pos']
                    dist = haversine(lon1, lat1, lon2, lat2)

                    graph.add_edge(node1, node2, weight=dist)
                    graph.add_edge(node2, node1, weight=dist)

    with open(pfile, "wb") as f:
        pickle.dump(graph, f)
#Latitude,Longitude
#source = (1.4293057,103.8351806)#yishun
#destination = (1.3509128,103.8479885)#bishan
source=(1.4173472,103.8329743)
destination=(1.4050934,103.9085724)
source_node = None
destination_node = None
src_acc = 0.010
des_acc = 0.010
min_dist_src = float('inf')
min_dist_des = float('inf')

for node_id, attributes in graph.nodes(data=True):
    lat, lon = attributes["pos"]
    temp1 = haversine(lon, lat, source[1], source[0])
    temp2 = haversine(lon, lat, destination[1], destination[0])
    if temp1 < min_dist_src and temp1 <= src_acc:
        source_node = node_id
        min_dist_src = temp1
    if temp2 < min_dist_des and temp2 <= des_acc:
        destination_node = node_id
        min_dist_des = temp2
while(source_node==None):
    src_acc+=0.001
    for node_id, attributes in graph.nodes(data=True):
        lat, lon = attributes["pos"]
        temp1 = haversine(lon, lat, source[1], source[0])
        if temp1 < min_dist_src and temp1 <= src_acc:
            source_node = node_id
            min_dist_src = temp1
while(destination_node==None):
    des_acc+=0.001
    for node_id, attributes in graph.nodes(data=True):
        lat, lon = attributes["pos"]
        temp2 = haversine(lon, lat, destination[1], destination[0])
        if temp2 < min_dist_des and temp2 <= des_acc:
            destination_node = node_id
            min_dist_des = temp2


shortest_path= AStar_Single.AStar(graph, source_node, destination_node, destination[0], destination[1])
eco_path=AStar_Eco.AStar(graph,source_node,destination_node,destination[0],destination[1])
print("Shortest path:", shortest_path)
geolocator = Nominatim(user_agent="ecoroutes_test")
test=[8620920513,
3893909401,
6191064918]
for n in test:
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
