import os
import pickle
import networkx as nx
from GraphFindingAlgos import AStar_Single

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


source = (1.4293057,103.8351806)#yishun
destination = (1.3509128,103.8479885)#bishan
# Specify the source and target nodes
node_source = ox.distance.nearest_nodes(graph, source[1], source[0])
node_target = ox.distance.nearest_nodes(graph, destination[1], destination[0])
temp=graph.nodes(node_source)
print(node_target)
print(node_source)

# Find the shortest path between the source and target nodes

#shortest_path=nx.shortest_path(graph, node_source, node_target, weight='length')
shortest_path=AStar_Single.AStar(graph,node_source,node_target,destination[0],destination[1])

# Print the shortest path
print("Shortest path:", shortest_path)
geolocator = Nominatim(user_agent="ecoroutes_test")
coordinates = []
for node in shortest_path[0]:
    node_data = graph.nodes[node]
    latitude, longitude = node_data['y'], node_data['x']
    location = geolocator.reverse((latitude, longitude), exactly_one=True)

    # Print the location name
    print("Location name:", location.address)
    coordinates.append((latitude, longitude))

# Print the coordinates
print("Coordinates:", coordinates)

# Plot the graph with the shortest path highlighted
fig, ax = ox.plot_graph_route(graph, shortest_path[0], route_linewidth=6, node_size=0, bgcolor='w')

# Customize the plot
ax.scatter(source[1], source[0], c='r', edgecolor='k', s=100, label='Source')
ax.scatter(destination[1], destination[0], c='g', edgecolor='k', s=100, label='Target')

# Add a legend
ax.legend()

# Show the plot
ox.plot.show(fig)