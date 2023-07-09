#OUTDATED

import osmnx as ox
from geopy.geocoders import Nominatim
from GraphFindingAlgos import Dijkstra_Router

place_name = "Singapore"
graph = ox.graph_from_place(place_name, network_type="drive")
print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))


source = (1.4295, 103.835)
destination = (1.4173, 103.8330)

# Specify the source and target nodes
node_source = ox.distance.nearest_nodes(graph, source[1], source[0])
node_target = ox.distance.nearest_nodes(graph, destination[1], destination[0])
print(node_target)
print(node_source)

# Find the shortest path between the source and target nodes

#shortest_path_correct = nx.shortest_path(graph, node_source, node_target, weight='length') Library function (Remove)
shortest_path= Dijkstra_Router.dijkstra(graph, node_source, node_target)

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