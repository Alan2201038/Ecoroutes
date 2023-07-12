import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar, Dijkstra
from GraphFindingAlgos import AStar_Eco
import math
import folium
import pandas as pd
from geopy.distance import geodesic
import time


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


carGraph = "car_graph.pickle"
mrtGraph = "mrt_graph.pickle"
matchesDict = "matches_dict.pickle"
# Add bus graph

south = 1.1646
west = 103.5879
north = 1.4769
east = 104.0942

# Create graph for car routes
if os.path.exists(carGraph):
    with open(carGraph, "rb") as f:
        car_Graph = pickle.load(f)
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
    car_Graph = nx.DiGraph()
    # First pass to add all nodes to graph as there might be cases where the edges come before the nodes
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lon = element["lon"]
            lat = element["lat"]
            car_Graph.add_node(node_id, pos=(lat, lon))
    for element in data["elements"]:
        if element["type"] == "way":
            node_ids = element["nodes"]
            if "oneway" in element["tags"]:
                oneway = element["tags"]["oneway"]
                if oneway == "yes":
                    # Add backwards connection for graphfinding algo to ignore illegal edges
                    # node index 0 will always be the FROM, index 1 is TO
                    node1 = node_ids[0]
                    node2 = node_ids[1]
                    lat1, lon1 = car_Graph.nodes[node1]['pos']
                    lat2, lon2 = car_Graph.nodes[node2]['pos']
                    dist = haversine(lon1, lat1, lon2, lat2)

                    car_Graph.add_edge(node2, node1, weight=dist, direction='backward')
            else:
                # Add bidirectional edge
                for i in range(len(node_ids) - 1):
                    node1 = node_ids[i]
                    node2 = node_ids[i + 1]
                    lat1, lon1 = car_Graph.nodes[node1]['pos']
                    lat2, lon2 = car_Graph.nodes[node2]['pos']
                    dist = haversine(lon1, lat1, lon2, lat2)

                    car_Graph.add_edge(node1, node2, weight=dist)
                    car_Graph.add_edge(node2, node1, weight=dist, direction='both')

    with open(carGraph, "wb") as f:
        pickle.dump(car_Graph, f)

# Create graph for mrt routes
if os.path.exists(mrtGraph):
    with open(mrtGraph, "rb") as f:
        mrt_Graph = pickle.load(f)
else:
    # Load the MRT station data
    df = pd.read_csv('MRT Stations.csv')

    # Create an empty graph
    mrt_Graph = nx.Graph()


    # Helper function to split station number into prefix and numeric part
    def split_stn_no(stn_no):
        prefix = ''.join(filter(str.isalpha, stn_no))
        num = ''.join(filter(str.isdigit, stn_no))
        return prefix, int(num) if num.isdigit() else None


    # Add a node for each station
    for index, row in df.iterrows():
        mrt_Graph.add_node(row['STN_NAME'], pos=(row['Latitude'], row['Longitude']))

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
            num2, node2 = stns[i + 1]
            if abs(num1 - num2) == 1:
                mrt_Graph.add_edge(node1, node2,
                                   weight=geodesic(mrt_Graph.nodes[node1]['pos'], mrt_Graph.nodes[node2]['pos']).m)

    # Manually add edges for Punggol and Sengkang to their connected LRT stations
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'SAM KEE LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'],
                                       mrt_Graph.nodes['SAM KEE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'SOO TECK LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'],
                                       mrt_Graph.nodes['SOO TECK LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'COVE LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'],
                                       mrt_Graph.nodes['COVE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'DAMAI LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'],
                                       mrt_Graph.nodes['DAMAI LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'CHENG LIM LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'],
                                       mrt_Graph.nodes['CHENG LIM LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'RENJONG LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'],
                                       mrt_Graph.nodes['RENJONG LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'COMPASSVALE LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'],
                                       mrt_Graph.nodes['COMPASSVALE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'RANGGUNG LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'],
                                       mrt_Graph.nodes['RANGGUNG LRT STATION']['pos']).m)

    # Manually add edges for Yew Tee and Kranji
    mrt_Graph.add_edge('YEW TEE MRT STATION', 'KRANJI MRT STATION',
                       weight=geodesic(mrt_Graph.nodes['YEW TEE MRT STATION']['pos'],
                                       mrt_Graph.nodes['KRANJI MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Botanic Gardens
    mrt_Graph.add_edge('CALDECOTT MRT STATION', 'BOTANIC GARDENS MRT STATION',
                       weight=geodesic(mrt_Graph.nodes['CALDECOTT MRT STATION']['pos'],
                                       mrt_Graph.nodes['BOTANIC GARDENS MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Stevens
    mrt_Graph.add_edge('CALDECOTT MRT STATION', 'STEVENS MRT STATION',
                       weight=geodesic(mrt_Graph.nodes['CALDECOTT MRT STATION']['pos'],
                                       mrt_Graph.nodes['STEVENS MRT STATION']['pos']).m)

    # Manually add edges for Marina Bay and Gardens By The Bay
    mrt_Graph.add_edge('MARINA BAY MRT STATION', 'GARDENS BY THE BAY MRT STATION',
                       weight=geodesic(mrt_Graph.nodes['MARINA BAY MRT STATION']['pos'],
                                       mrt_Graph.nodes['GARDENS BY THE BAY MRT STATION']['pos']).m)

    # Manually add edges for Bukit Panjang and Senja
    mrt_Graph.add_edge('BUKIT PANJANG MRT STATION', 'SENJA LRT STATION',
                       weight=geodesic(mrt_Graph.nodes['BUKIT PANJANG MRT STATION']['pos'],
                                       mrt_Graph.nodes['SENJA LRT STATION']['pos']).m)

    neighbors = mrt_Graph.neighbors('LABRADOR PARK MRT STATION')

    with open(mrtGraph, "wb") as f:
        pickle.dump(mrt_Graph, f)



df = pd.read_excel('..\\Data\\MRTs_V2.0.xlsx')
df_list = df.to_dict(orient='records')
if os.path.exists(matchesDict):
    with open(matchesDict, "rb") as f:
        matches = pickle.load(f)
else:
    MRTDict = {}
    matches = {}


    for stn in df_list:
        latitude, longitude = stn["Lat"], stn["Lon"]
        temp_node_acc = 0.009
        temp_node = None
        min_dist = float('inf')
        while temp_node==None:
            temp_node_acc+=0.001
            for node in car_Graph.nodes:
                curr_val = car_Graph.nodes[node]["pos"]
                curr_lat,curr_lon=curr_val[0],curr_val[1]
                temp_haversine=haversine(longitude, latitude, curr_lon, curr_lat)
                if temp_haversine< min_dist and temp_haversine<temp_node_acc:
                    temp_node= node
                    min_dist=temp_haversine
        matches[stn["Name"]]=temp_node
    with open(matchesDict, "wb") as f:
        pickle.dump(matches, f)

for mrt_stns, nodeid in matches.items():
    neighbors = mrt_Graph.neighbors(mrt_stns)
    for neighbor in neighbors:
        edge_data = (mrt_Graph.get_edge_data(mrt_stns, neighbor)['weight']) / 1000
        car_Graph.add_edge(nodeid, matches[neighbor], weight=edge_data, transportation="Mrt",direction='both')
for stn in df_list:
    if stn['Name']=="KHATIB MRT STATION":
        des_lat,des_lon=stn["Lat"],stn["Lon"]
path, total_distance = AStar_CarMRT.AStar(car_Graph, matches['YISHUN MRT STATION'], matches['KHATIB MRT STATION'],des_lat,des_lon)
