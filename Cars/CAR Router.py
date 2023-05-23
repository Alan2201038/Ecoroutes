import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim

place_name = "Singapore"
graph = ox.graph_from_place(place_name, network_type="drive")


target_location = (1.4295, 103.835)
target_locationB = (1.4173, 103.8330)

# Specify the source and target nodes
node_source = ox.distance.nearest_nodes(graph, target_location[1], target_location[0])
node_target = ox.distance.nearest_nodes(graph, target_locationB[1], target_locationB[0])

# Find the shortest path between the source and target nodes
#TO DO: REPLACE WITH OWN DIJSTRKA ALGORITHM
shortest_path = nx.shortest_path(graph, node_source, node_target, weight='length')

# Print the shortest path
print("Shortest path:", shortest_path)
geolocator = Nominatim(user_agent="ecoroutes_test")
coordinates = []
for node in shortest_path:
    node_data = graph.nodes[node]
    latitude, longitude = node_data['y'], node_data['x']
    location = geolocator.reverse((latitude, longitude), exactly_one=True)

    # Print the location name
    print("Location name:", location.address)
    coordinates.append((latitude, longitude))

# Print the coordinates
print("Coordinates:", coordinates)


# Create a geocoder instance


# Specify the latitude and longitude coordinates
latitude, longitude = 1.4303601, 103.8352969

# Reverse geocode the coordinates to obtain the location name
