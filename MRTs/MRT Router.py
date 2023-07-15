import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pickle
import os
import GraphFindingAlgos.AStar

mrtGraph= "MRT_Pickle_Graph"

if os.path.exists(mrtGraph):
    with open(mrtGraph, "rb") as f:
        G = pickle.load(f)
        print("True")
else:
    # Load the MRT station data
    df = pd.read_csv('MRT Stations.csv')

    # Create an empty graph
    G = nx.Graph()

# Helper function to split station number into prefix and numeric part
    def split_stn_no(stn_no):
        prefix = ''.join(filter(str.isalpha, stn_no))
        num = ''.join(filter(str.isdigit, stn_no))
        return prefix, int(num) if num.isdigit() else None

    # Add a node for each station
    for index, row in df.iterrows():
        G.add_node(row['STN_NAME'], pos=(row['Latitude'], row['Longitude']))

    # Create a dictionary to store connections
    connections = {}

    # Add connections for each station
    for index, row in df.iterrows():
        stn_nos = row['STN_NO'].split('/')
        for stn_no in stn_nos:
            prefix, num = split_stn_no(stn_no)
            if prefix not in connections:
                connections[prefix] = []
            connections[prefix].append((num, row['STN_NAME']))

    # Special cases for Punggol and Sengkang
    connections['PTC'] = [(1, 'PUNGGOL MRT STATION'), (7, 'PUNGGOL MRT STATION')]
    connections['STC'] = [(1, 'SENGKANG MRT STATION'), (5, 'SENGKANG MRT STATION')]

    # Add edges for each pair of stations on the same line with consecutive numbers
    for prefix, stns in connections.items():
        stns.sort()
        for i in range(len(stns) - 1):
            num1, node1 = stns[i]
            num2, node2 = stns[i+1]
            if abs(num1 - num2) == 1:
                G.add_edge(node1, node2, weight=geodesic(G.nodes[node1]['pos'], G.nodes[node2]['pos']).m)

# Manually add edges for Punggol and Sengkang to their connected LRT stations
    G.add_edge('PUNGGOL MRT STATION', 'SAM KEE LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SAM KEE LRT STATION']['pos']).m)
    G.add_edge('PUNGGOL MRT STATION', 'SOO TECK LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SOO TECK LRT STATION']['pos']).m)
    G.add_edge('PUNGGOL MRT STATION', 'COVE LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['COVE LRT STATION']['pos']).m)
    G.add_edge('PUNGGOL MRT STATION', 'DAMAI LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['DAMAI LRT STATION']['pos']).m)
    G.add_edge('SENGKANG MRT STATION', 'CHENG LIM LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['CHENG LIM LRT STATION']['pos']).m)
    G.add_edge('SENGKANG MRT STATION', 'RENJONG LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RENJONG LRT STATION']['pos']).m)
    G.add_edge('SENGKANG MRT STATION', 'COMPASSVALE LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['COMPASSVALE LRT STATION']['pos']).m)
    G.add_edge('SENGKANG MRT STATION', 'RANGGUNG LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RANGGUNG LRT STATION']['pos']).m)

    # Manually add edges for Yew Tee and Kranji
    G.add_edge('YEW TEE MRT STATION', 'KRANJI MRT STATION', weight=geodesic(G.nodes['YEW TEE MRT STATION']['pos'], G.nodes['KRANJI MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Botanic Gardens
    G.add_edge('CALDECOTT MRT STATION', 'BOTANIC GARDENS MRT STATION', weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'], G.nodes['BOTANIC GARDENS MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Stevens
    G.add_edge('CALDECOTT MRT STATION', 'STEVENS MRT STATION', weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'], G.nodes['STEVENS MRT STATION']['pos']).m)

    # Manually add edges for Marina Bay and Gardens By The Bay
    G.add_edge('MARINA BAY MRT STATION', 'GARDENS BY THE BAY MRT STATION', weight=geodesic(G.nodes['MARINA BAY MRT STATION']['pos'], G.nodes['GARDENS BY THE BAY MRT STATION']['pos']).m)

    # Manually add edges for Bukit Panjang and Senja
    G.add_edge('BUKIT PANJANG MRT STATION', 'SENJA LRT STATION', weight=geodesic(G.nodes['BUKIT PANJANG MRT STATION']['pos'], G.nodes['SENJA LRT STATION']['pos']).m)

    with open(mrtGraph, "wb") as f:
        pickle.dump(G, f)

print(len(G.nodes))
def dist(a, b):
    (x1, y1) = G.nodes[a]['pos']
    (x2, y2) = G.nodes[b]['pos']
    return geodesic((x1, y1), (x2, y2)).m

#A* algo

def astar(start, goal):
    def heuristic(a, b):
        (x1, y1) = G.nodes[a]['pos']
        (x2, y2) = G.nodes[b]['pos']
        return geodesic((x1, y1), (x2, y2)).m

    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    closed_set = set()
    open_set = set([start])
    came_from = {}
    g_score = {node: float('inf') for node in G.nodes}
    g_score[start] = 0
    f_score = {node: float('inf') for node in G.nodes}
    f_score[start] = heuristic(start, goal)

    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == goal:
            return reconstruct_path(came_from, current), g_score[goal]

        open_set.remove(current)
        closed_set.add(current)

        for neighbor in G.neighbors(current):
            tentative_g_score = g_score[current] + G.edges[current, neighbor]['weight']
            if neighbor in closed_set and tentative_g_score >= g_score[neighbor]:
                continue
            if neighbor not in open_set or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                open_set.add(neighbor)

    return None, float('inf')


path,total_distance = GraphFindingAlgos.AStar.AStar(G, 'YIO CHU KANG MRT STATION', 'DAMAI LRT STATION',1.4050934,103.9085724)

#path, total_distance = astar('WOODLANDS MRT STATION', 'BUGIS MRT STATION')
print(" -> ".join(path))

print(f"Total distance: {total_distance/1000} km") #not accurate cause this is straight line distance from one node to the next

# Calculate time taken for distance travelled
time_taken = total_distance/1000 / 45  # Time taken in hours

# Calculate additional time for stops
additional_time = len(path) / 60  # Time for stops in hours

# Add the two times together
total_time = time_taken + additional_time

# Convert the decimal hours to hours and minutes
hours = int(total_time)
minutes = (total_time - hours) * 60

print(f"Estimated time for the route: {hours} hours and {int(minutes)} minutes")

carbon_emissions = total_distance/1000 * 0.0132
print(f"Carbon emissions: {carbon_emissions} kg CO2")

# Extract the positions of the nodes for the plot
pos = nx.get_node_attributes(G, 'pos')

# Convert positions from lat/long to an easier-to-visualize system
# This is a simple linear conversion that might distort distances, but it will work for this visualization
pos = {node: (long, -lat) for node, (lat, long) in pos.items()}

# Draw the graph, with nodes labeled by their names
nx.draw_networkx(G, pos, with_labels=True, node_size=20, font_size=6)

# Flip the y-axis
plt.gca().invert_yaxis()

# Display the plot
plt.show()