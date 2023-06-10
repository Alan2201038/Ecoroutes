import requests
import networkx as nx
import matplotlib.pyplot as plt

# Define the bounding box coordinates for Singapore
south = 1.1646
west = 103.5879
north = 1.4769
east = 104.0942

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

for element in data["elements"]:
    if element["type"] == "node":
        node_id = element["id"]
        lon = element["lon"]
        lat = element["lat"]
        graph.add_node(node_id, pos=(lon, lat))
    elif element["type"] == "way":
        node_ids = element["nodes"]
        for i in range(len(node_ids) - 1):
            node1 = node_ids[i]
            node2 = node_ids[i + 1]

            graph.add_edge(node1, node2)

print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))

# Extract the positions of the nodes for the plot
pos = nx.get_node_attributes(graph, 'pos')

# Convert positions from lat/long to an easier-to-visualize system
# This is a simple linear conversion that might distort distances, but it will work for this visualization
pos = {node_id: (lon, -lat) for node_id, (lat, lon) in pos.items()}
print("Drawing Graph")
# Draw the graph, with nodes labeled by their names
nx.draw_networkx(graph, pos, with_labels=True, node_size=20, font_size=6)
print("Ending of drawing Graph")
# Flip the y-axis
plt.gca().invert_yaxis()

# Display the plot
plt.show()