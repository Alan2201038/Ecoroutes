import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar,Dijkstra
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
            graph.add_node(node_id, pos=(lon, lat))
    for element in data["elements"]:
        if element["type"] == "way":
            node_ids = element["nodes"]
            for i in range(len(node_ids) - 1):
                node1 = node_ids[i]
                node2 = node_ids[i + 1]
                lon1, lat1 = graph.nodes[node1]['pos']
                lon2, lat2 = graph.nodes[node2]['pos']
                dist=haversine(lat1,lon1,lat2,lon2)

                graph.add_edge(node1, node2,weight=dist)

    with open(pfile, "wb") as f:
        pickle.dump(graph, f)

print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))

#Long,Lat
source = (103.835,1.4295)
destination = (103.8330,1.4173)

source_node = None
destination_node = None

for node_id, attributes in graph.nodes(data=True):
    lon, lat = attributes["pos"]
    temp1=haversine(lon, lat, source[0], source[1])
    temp2=haversine(lon, lat, destination[0], destination[1])
    if  temp1<= 0.015:
        source_node=node_id
    if  temp2<= 0.015:
        destination_node=node_id
shortest_path=Dijkstra.dijkstra(graph,source_node,destination_node)
print("Shortest path:", shortest_path)
geolocator = Nominatim(user_agent="ecoroutes_test")
for n in shortest_path[0]:
    node_data = graph.nodes[n]["pos"]
    latitude, longitude = node_data[1], node_data[0]
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    print("Location name:", location.address)


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