import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx

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

    with open(pfile, "wb") as f:
        pickle.dump(graph, f)

print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))

# Draw the graph
plt.figure(figsize=(10, 10))
pos = nx.get_node_attributes(graph, 'pos')
nx.draw_networkx(graph, pos, node_size=1, node_color='black', edge_color='w', alpha=0.5, with_labels=False)

# Adjust plot settings
plt.xlim(west, east)
plt.ylim(south, north)
plt.axis('off')

# Show the plot
plt.show()