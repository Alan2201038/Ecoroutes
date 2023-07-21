import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pickle
import sys
import os

# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

import GraphFindingAlgos.AStar_Eco as AStar_Eco
from GUI import Map

def create_map_graph():

    mrtGraph= "Data\\MRT_Pickle_Graph"

    if os.path.exists(mrtGraph):
        with open(mrtGraph, "rb") as f:
            G = pickle.load(f)
    else:
        # Load the MRT station data

        df = pd.read_csv('Data\\MRT Stations.csv')
        df_timing=pd.read_csv('Data\\mrt_time.csv')

        # Create an empty graph
        G = nx.MultiDiGraph()

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
                    dist=geodesic(G.nodes[node1]['pos'], G.nodes[node2]['pos']).m
                    G.add_edge(node1, node2,weight=dist)
                    G.add_edge(node2,node1,weight=dist)


        # Manually add edges for Punggol and Sengkang to their connected LRT stations
        G.add_edge('PUNGGOL MRT STATION', 'SAM KEE LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SAM KEE LRT STATION']['pos']).m)
        G.add_edge('PUNGGOL MRT STATION', 'SOO TECK LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SOO TECK LRT STATION']['pos']).m)
        G.add_edge('PUNGGOL MRT STATION', 'COVE LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['COVE LRT STATION']['pos']).m)
        G.add_edge('PUNGGOL MRT STATION', 'DAMAI LRT STATION', weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['DAMAI LRT STATION']['pos']).m)
        G.add_edge('SENGKANG MRT STATION', 'CHENG LIM LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['CHENG LIM LRT STATION']['pos']).m)
        G.add_edge('SENGKANG MRT STATION', 'RENJONG LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RENJONG LRT STATION']['pos']).m)
        G.add_edge('SENGKANG MRT STATION', 'COMPASSVALE LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['COMPASSVALE LRT STATION']['pos']).m)
        G.add_edge('SENGKANG MRT STATION', 'RANGGUNG LRT STATION', weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RANGGUNG LRT STATION']['pos']).m)

        G.add_edge('SAM KEE LRT STATION', 'PUNGGOL MRT STATION',
                weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SAM KEE LRT STATION']['pos']).m)

        G.add_edge('SOO TECK LRT STATION', 'PUNGGOL MRT STATION',
                weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['SOO TECK LRT STATION']['pos']).m)

        G.add_edge('COVE LRT STATION', 'PUNGGOL MRT STATION',
                weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['COVE LRT STATION']['pos']).m)

        G.add_edge('DAMAI LRT STATION', 'PUNGGOL MRT STATION',
                weight=geodesic(G.nodes['PUNGGOL MRT STATION']['pos'], G.nodes['DAMAI LRT STATION']['pos']).m)

        G.add_edge('CHENG LIM LRT STATION', 'SENGKANG MRT STATION',
                weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['CHENG LIM LRT STATION']['pos']).m)

        G.add_edge('RENJONG LRT STATION', 'SENGKANG MRT STATION',
                weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RENJONG LRT STATION']['pos']).m)

        G.add_edge('COMPASSVALE LRT STATION', 'SENGKANG MRT STATION',
                weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['COMPASSVALE LRT STATION']['pos']).m)

        G.add_edge('RANGGUNG LRT STATION', 'SENGKANG MRT STATION',
                weight=geodesic(G.nodes['SENGKANG MRT STATION']['pos'], G.nodes['RANGGUNG LRT STATION']['pos']).m)


        G.add_edge('YEW TEE MRT STATION', 'KRANJI MRT STATION', weight=geodesic(G.nodes['YEW TEE MRT STATION']['pos'], G.nodes['KRANJI MRT STATION']['pos']).m)
        G.add_edge('KRANJI MRT STATION', 'YEW TEE MRT STATION',
                weight=geodesic(G.nodes['YEW TEE MRT STATION']['pos'], G.nodes['KRANJI MRT STATION']['pos']).m)

        G.add_edge('CALDECOTT MRT STATION', 'BOTANIC GARDENS MRT STATION', weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'], G.nodes['BOTANIC GARDENS MRT STATION']['pos']).m)
        G.add_edge('BOTANIC GARDENS MRT STATION', 'CALDECOTT MRT STATION',
                weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'],
                                G.nodes['BOTANIC GARDENS MRT STATION']['pos']).m)

        G.add_edge('CALDECOTT MRT STATION', 'STEVENS MRT STATION', weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'], G.nodes['STEVENS MRT STATION']['pos']).m)
        G.add_edge('STEVENS MRT STATION', 'CALDECOTT MRT STATION',
                weight=geodesic(G.nodes['CALDECOTT MRT STATION']['pos'], G.nodes['STEVENS MRT STATION']['pos']).m)

        G.add_edge('MARINA BAY MRT STATION', 'GARDENS BY THE BAY MRT STATION', weight=geodesic(G.nodes['MARINA BAY MRT STATION']['pos'], G.nodes['GARDENS BY THE BAY MRT STATION']['pos']).m)
        G.add_edge('GARDENS BY THE BAY MRT STATION', 'MARINA BAY MRT STATION',
                weight=geodesic(G.nodes['MARINA BAY MRT STATION']['pos'],
                                G.nodes['GARDENS BY THE BAY MRT STATION']['pos']).m)


        G.add_edge('BUKIT PANJANG MRT STATION', 'SENJA LRT STATION', weight=geodesic(G.nodes['BUKIT PANJANG MRT STATION']['pos'], G.nodes['SENJA LRT STATION']['pos']).m)
        G.add_edge('SENJA LRT STATION', 'BUKIT PANJANG MRT STATION',
                weight=geodesic(G.nodes['BUKIT PANJANG MRT STATION']['pos'], G.nodes['SENJA LRT STATION']['pos']).m)

        G.add_edge('HILLVIEW MRT STATION','BEAUTY WORLD MRT STATION',weight=geodesic(G.nodes['HILLVIEW MRT STATION']['pos'], G.nodes['BEAUTY WORLD MRT STATION']['pos']).m)
        G.add_edge('BEAUTY WORLD MRT STATION', 'HILLVIEW MRT STATION',
                weight=geodesic(G.nodes['HILLVIEW MRT STATION']['pos'], G.nodes['BEAUTY WORLD MRT STATION']['pos']).m)

        for index, row in df_timing.iterrows():
            start_node = row['Start']
            end_node = row['End']
            duration = row['Duration']
            if G.has_edge(start_node, end_node):
                G.edges[start_node, end_node,0]['duration'] = duration
                G.edges[start_node,end_node,0]['key']=f"MRT_{start_node}_{end_node}"
                G.edges[end_node, start_node,0]['duration'] = duration
                G.edges[end_node, start_node,0]['key'] = f"MRT_{end_node}_{start_node}"
            else:
                print(f"Warning: No edge found between {start_node} and {end_node}")

        with open(mrtGraph, "wb") as f:
            pickle.dump(G, f)

        print(G.nodes)
        print(len(G.edges))

    return G

def Mrt_Route(start, end):
    path_v = []
    G = create_map_graph()
    path_v = AStar_Eco.AStar(G, start, end)
    print(path_v)

    map_html = Map.draw_map(path_v[0])

    return map_html