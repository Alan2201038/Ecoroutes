import pandas as pd
# from MRT_data_csv import write_Dataframe
import networkx as nx
import matplotlib.pyplot as plt
import math

def create_graph(filename):

    # Create a graph object
    G = nx.Graph()

    # data = write_Data()
    # data_test = write_Dataframe()
    # df = pd.DataFrame(data_test)


    df = pd.read_csv(filename)
    split_df = df['STN_NO'].str.split('/', expand=True).stack().reset_index(level=1, drop=True).rename('STN_NO')

    # Concatenate the split DataFrame with the duplicated columns
    df = pd.concat([df.drop('STN_NO', axis=1), split_df], axis=1).reset_index(drop=True)

    # Create a new 'line' column by extracting non-digit characters
    df['line'] = df['STN_NO'].str.extract('(\D+)', expand=False)

    # Create a new 'order' column by extracting digit characters
    df['order'] = df['STN_NO'].str.extract('(\d+)', expand=False).fillna(0)
    df['order'] = pd.to_numeric(df['order'])

    # Add a node for each station
    for  index,row in df.iterrows():
        G.add_node(row['STN_NAME'], pos=(row['Latitude'], row['Longitude'],row['STN_NO']))

    # Add edges based on the same line value and order
    for line in set(df['line']):
        line_stations = df[df['line'] == line]
        # print(line_stations)
        sorted_stations = line_stations.sort_values('order',ascending=True)
        
        # print(sorted_stations)
        # Iterate over the sorted stations and create edges
        for i in range(len(sorted_stations) - 1):
            current_station = sorted_stations.iloc[i]
            next_station = sorted_stations.iloc[i + 1]
            # Add the edge between the current station and the next station to the graph
            G.add_edge(current_station['STN_NAME'], next_station['STN_NAME'])

    #add edge
    G.add_edge('SENGKANG MRT STATION','RENJONG LRT STATION')
    G.add_edge('SENGKANG MRT STATION','CHENG LIM LRT STATION')
    G.add_edge('SENGKANG MRT STATION','COMPASSVALE LRT STATION')
    G.add_edge('SENGKANG MRT STATION','RANGGUNG LRT STATION')
    G.add_edge('PUNGGOL MRT STATION','SOO TECK LRT STATION')
    G.add_edge('PUNGGOL MRT STATION','SAM KEE LRT STATION')
    G.add_edge('PUNGGOL MRT STATION','DAMAI LRT STATION')
    G.add_edge('PUNGGOL MRT STATION','COVE LRT STATION')
    G.add_edge('BUKIT PANJANG MRT STATION','SENJA LRT STATION')


    # Print nodes and their corresponding edges
    # for node in G.nodes():
    #     edges = list(G.edges(node))
    #     if edges:
    #         print("Node:", node)
    #         print("Edges:", edges)
    #         print()
    pos = nx.get_node_attributes(G, 'pos')
    return G

def plot_graph(G,path):
    # Get node positions (latitude and longitude)
    pos = nx.get_node_attributes(G, 'pos')

    # Extract the latitude and longitude as separate lists
    lats = [pos[node][0] for node in G.nodes()]
    lons = [pos[node][1] for node in G.nodes()]

    # Plot the nodes
    plt.figure(figsize=(8, 6))
    plt.scatter(lons, lats, s=50, c='lightblue', edgecolors='gray', alpha=0.8)

    # Add labels to the nodes
    for node, (lat, lon,lo) in pos.items():
        plt.text(lon, lat, lo, ha='center', va='center', fontsize=8)
    
     # Add edges and connect them
    for u, v in G.edges():
        plt.plot([pos[u][1], pos[v][1]], [pos[u][0], pos[v][0]], color='gray', linewidth=1, alpha=0.5)

    # Highlight the path if provided
    if path:
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        for u, v in path_edges:
            plt.plot([pos[u][1], pos[v][1]], [pos[u][0], pos[v][0]], color='red', linewidth=2)


    # Customize the plot
    plt.axis('off')
    plt.title('Nodes plotted based on Latitude and Longitude')

    # Adjust the plot layout
    plt.tight_layout()

    # Display the plot
    plt.show()

def shortest_path(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return path
    if start not in graph.nodes:
        return None
    shortest = None
    for node in graph.neighbors(start):
        if node not in path:
            new_path = shortest_path(graph, node, end, path)
            if new_path:
                if not shortest or len(new_path) < len(shortest):
                    shortest = new_path
    return shortest

def all_paths(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph.nodes:
        return []
    paths = []
    for node in graph.neighbors(start):
        if node not in path:
            new_paths = all_paths(graph, node, end, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths

G =create_graph('mrt_stations_test.csv')
# Call the function to plot the nodes based on their coordinates


# Usage example to find the shortest path between two stations
start_station = 'WOODLANDS MRT STATION'
end_station = 'RAFFLES PLACE MRT STATION'

# Call the modified shortest_path function
path = shortest_path(G, start_station, end_station)
# path2 = all_paths(G,start_station,end_station)

# for path in path2:
#     print('->'.join(path))

# Print the shortest path
if path:
    print('Shortest path:', ' -> '.join(path))
else:
    print('No path found between the stations.')

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on the Earth's surface using the Haversine formula.
    """
    R = 6371  # Radius of the Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c  # Distance in kilometers
    return distance

total_distance = 0

for i in range(len(path) - 1):
    current_node = path[i]
    next_node = path[i + 1]

    current_pos = G.nodes[current_node]['pos'][:2]
    next_pos = G.nodes[next_node]['pos'][:2]

    distance = calculate_distance(current_pos[0], current_pos[1], next_pos[0], next_pos[1])
    total_distance += distance

print("Total distance:", total_distance, "km")

# Calculate time taken for distance travelled
time_taken = total_distance/ 45  # Time taken in hours

# Calculate additional time for stops
additional_time = len(path) / 60  # Time for stops in hours

# Add the two times together
total_time = time_taken + additional_time

# Convert the decimal hours to hours and minutes
hours = int(total_time)
minutes = (total_time - hours) * 60

print(f"Estimated time for the route: {hours} hours and {int(minutes)} minutes")

carbon_emissions = total_distance * 0.0132
print(f"Carbon emissions: {carbon_emissions} kg CO2")
# plot_graph(G,path)

