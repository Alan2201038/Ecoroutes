import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar,Dijkstra
import math
import RouteGUI as RouteGUI
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
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

carGraph = "car_graph.pickle"
mrtGraph = "mrt_graph.pickle"
#Add bus graph

south = 1.1646
west = 103.5879
north = 1.4769
east = 104.0942

#Create graph for car routes
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
    car_Graph = nx.Graph()
    #First pass to add all nodes to graph as there might be cases where the edges come before the nodes
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lon = element["lon"]
            lat = element["lat"]
            car_Graph.add_node(node_id, pos=(lat, lon))
    for element in data["elements"]:
        if element["type"] == "way":
            node_ids = element["nodes"]
            for i in range(len(node_ids) - 1):
                node1 = node_ids[i]
                node2 = node_ids[i + 1]
                lat1, lon1 = car_Graph.nodes[node1]['pos']
                lat2, lon2 = car_Graph.nodes[node2]['pos']
                dist = haversine(lon1, lat1, lon2, lat2)

                car_Graph.add_edge(node1, node2, weight=dist)

    with open(carGraph, "wb") as f:
        pickle.dump(car_Graph, f)

#Create graph for mrt routes
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
            num2, node2 = stns[i+1]
            if abs(num1 - num2) == 1:
                mrt_Graph.add_edge(node1, node2, weight=geodesic(mrt_Graph.nodes[node1]['pos'], mrt_Graph.nodes[node2]['pos']).m)

# Manually add edges for Punggol and Sengkang to their connected LRT stations
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'SAM KEE LRT STATION', weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'], mrt_Graph.nodes['SAM KEE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'SOO TECK LRT STATION', weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'], mrt_Graph.nodes['SOO TECK LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'COVE LRT STATION', weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'], mrt_Graph.nodes['COVE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('PUNGGOL MRT STATION', 'DAMAI LRT STATION', weight=geodesic(mrt_Graph.nodes['PUNGGOL MRT STATION']['pos'], mrt_Graph.nodes['DAMAI LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'CHENG LIM LRT STATION', weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'], mrt_Graph.nodes['CHENG LIM LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'RENJONG LRT STATION', weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'], mrt_Graph.nodes['RENJONG LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'COMPASSVALE LRT STATION', weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'], mrt_Graph.nodes['COMPASSVALE LRT STATION']['pos']).m)
    mrt_Graph.add_edge('SENGKANG MRT STATION', 'RANGGUNG LRT STATION', weight=geodesic(mrt_Graph.nodes['SENGKANG MRT STATION']['pos'], mrt_Graph.nodes['RANGGUNG LRT STATION']['pos']).m)

    # Manually add edges for Yew Tee and Kranji
    mrt_Graph.add_edge('YEW TEE MRT STATION', 'KRANJI MRT STATION', weight=geodesic(mrt_Graph.nodes['YEW TEE MRT STATION']['pos'], mrt_Graph.nodes['KRANJI MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Botanic Gardens
    mrt_Graph.add_edge('CALDECOTT MRT STATION', 'BOTANIC GARDENS MRT STATION', weight=geodesic(mrt_Graph.nodes['CALDECOTT MRT STATION']['pos'], mrt_Graph.nodes['BOTANIC GARDENS MRT STATION']['pos']).m)

    # Manually add edges for Caldecott and Stevens
    mrt_Graph.add_edge('CALDECOTT MRT STATION', 'STEVENS MRT STATION', weight=geodesic(mrt_Graph.nodes['CALDECOTT MRT STATION']['pos'], mrt_Graph.nodes['STEVENS MRT STATION']['pos']).m)

    # Manually add edges for Marina Bay and Gardens By The Bay
    mrt_Graph.add_edge('MARINA BAY MRT STATION', 'GARDENS BY THE BAY MRT STATION', weight=geodesic(mrt_Graph.nodes['MARINA BAY MRT STATION']['pos'], mrt_Graph.nodes['GARDENS BY THE BAY MRT STATION']['pos']).m)

    # Manually add edges for Bukit Panjang and Senja
    mrt_Graph.add_edge('BUKIT PANJANG MRT STATION', 'SENJA LRT STATION', weight=geodesic(mrt_Graph.nodes['BUKIT PANJANG MRT STATION']['pos'], mrt_Graph.nodes['SENJA LRT STATION']['pos']).m)

    with open(mrtGraph, "wb") as f:
        pickle.dump(mrt_Graph, f)



MRTDict={}
#matches={'LABRADOR PARK MRT STATION': 6483278412, 'HARBOURFRONT MRT STATION': 10554032471, 'TELOK BLANGAH MRT STATION': 9959134482, 'TUAS CRESCENT MRT STATION': 5254927337, 'PASIR PANJANG MRT STATION': 10687458220, 'KENT RIDGE MRT STATION': 4375159026, 'ONE-NORTH MRT STATION': 7919213952, 'BUONA VISTA MRT STATION': 10886417165, 'COMMONWEALTH MRT STATION': 6182657602, 'HOLLAND VILLAGE MRT STATION': 6198863449, 'FARRER ROAD MRT STATION': 5227091715, 'TAN KAH KEE MRT STATION': 9597538681, 'BOON LAY MRT STATION': 5156488174, 'LAKESIDE MRT STATION': 5254900998, 'CHINESE GARDEN MRT STATION': 5254896539, 'BUKIT BATOK MRT STATION': 1994929042, 'TECK WHYE LRT STATION': 5256753565, 'BEAUTY WORLD MRT STATION': 7794813304, 'KING ALBERT PARK MRT STATION': 2085358332, 'SIXTH AVENUE MRT STATION': 10269595977, 'HUME MRT STATION': 9159993136, 'HILLVIEW MRT STATION': 5268524361, 'CASHEW MRT STATION': 7575088008, 'BUKIT PANJANG MRT STATION': 3942108186, 'PETIR LRT STATION': 7975724596, 'CHOA CHU KANG MRT STATION': 8340706700, 'JELAPANG LRT STATION': 9163207786, 'FAJAR LRT STATION': 9314479525, 'WOODLANDS SOUTH MRT STATION': 5258212269, 'WOODLANDS NORTH MRT STATION': 7125270713, 'REDHILL MRT STATION': 6214349893, 'HAVELOCK MRT STATION': 1944141246, 'GREAT WORLD MRT STATION': 9559603409, 'MAXWELL MRT STATION': 9559521720, 'CHINATOWN MRT STATION': 7029616642, 'DOWNTOWN MRT STATION': 2620921752, 'MARINA BAY MRT STATION': 10000726307, 'SHENTON WAY MRT STATION': 10177596814, 'RAFFLES PLACE MRT STATION': 1831853796, 'BAYFRONT MRT STATION': 6449623751, 'FORT CANNING MRT STATION': 7882974507, 'CLARKE QUAY MRT STATION': 8192613845, 'SOMERSET MRT STATION': 7915702370, 'ESPLANADE MRT STATION': 1683121652, 'PROMENADE MRT STATION': 5846583670, 'BRAS BASAH MRT STATION': 7863922616, 'BENCOOLEN MRT STATION': 7871959913, 'BUGIS MRT STATION': 6880702593, 'NAPIER MRT STATION': 6774268611, 'BOTANIC GARDENS MRT STATION': 5138687581, 'STEVENS MRT STATION': 9519222687, 'NEWTON MRT STATION': 6094720070, 'LITTLE INDIA MRT STATION': 8064193287, 'JALAN BESAR MRT STATION': 8006102762, 'FARRER PARK MRT STATION': 6919370869, 'NOVENA MRT STATION': 2660957655, 'NICOLL HIGHWAY MRT STATION': 6333597582, 'LAVENDER MRT STATION': 5272808156, 'KALLANG MRT STATION': 2391161888, 'BOON KENG MRT STATION': 5120876586, 'GEYLANG BAHRU MRT STATION': 5724846128, 'DAKOTA MRT STATION': 5286745324, 'MACPHERSON MRT STATION': 6334123186, 'KEMBANGAN MRT STATION': 7682168131, 'TOA PAYOH MRT STATION': 9838930791, 'CALDECOTT MRT STATION': 4594336925, 'BRADDELL MRT STATION': 8073614067, 'MARYMOUNT MRT STATION': 5968328742, 'BISHAN MRT STATION': 1994956059, 'UPPER THOMSON MRT STATION': 5648108171, 'BRIGHT HILL MRT STATION': 5175569981, 'MAYFLOWER MRT STATION': 5176595951, 'POTONG PASIR MRT STATION': 7035042242, 'WOODLEIGH MRT STATION': 6028825509, 'LORONG CHUAN MRT STATION': 8086940233, 'SERANGOON MRT STATION': 2441723247, 'BARTLEY MRT STATION': 7645954799, 'KOVAN MRT STATION': 4711963981, 'HOUGANG MRT STATION': 8170649184, 'TAMPINES WEST MRT STATION': 8236358631, 'TANAH MERAH MRT STATION': 10873214590, 'UPPER CHANGI MRT STATION': 6969106452, 'TAMPINES MRT STATION': 7684664576, 'TAMPINES EAST MRT STATION': 4427352120, 'PASIR RIS MRT STATION': 5240338012, 'CHANGI AIRPORT MRT STATION': 10195284736, 'LENTOR MRT STATION': 4591499988, 'YIO CHU KANG MRT STATION': 4849784927, 'YISHUN MRT STATION': 6649603955, 'LAYAR LRT STATION': 3893909403, 'TONGKANG LRT STATION': 7045415711, 'THANGGAM LRT STATION': 6033280630, 'KUPANG LRT STATION': 6191064960, 'RANGGUNG LRT STATION': 8183331056, 'RENJONG LRT STATION': 6191064933, 'KANGKAR LRT STATION': 8193413828, 'BAKAU LRT STATION': 7912584273, 'RUMBIA LRT STATION': 6192761652, 'FARMWAY LRT STATION': 8145456744, 'CHENG LIM LRT STATION': 6572225287, 'COMPASSVALE LRT STATION': 8181792554, 'COVE LRT STATION': 7603649103, 'MERIDIAN LRT STATION': 8250692199, 'PUNGGOL MRT STATION': 1712383724, 'OASIS LRT STATION': 8250414129, 'SUMANG LRT STATION': 6191130310, 'NIBONG LRT STATION': 6192558591, 'SAMUDERA LRT STATION': 1167584100, 'CANBERRA MRT STATION': 8663881368, 'RIVIERA LRT STATION': 4713507381, 'KADALOOR LRT STATION': 6192622759}
matches={}
for node in mrt_Graph.nodes:
    temp_values=mrt_Graph.nodes[node]["pos"]
    MRTDict[temp_values]=node
print(len(MRTDict.keys()))
print(MRTDict)
for node in car_Graph.nodes:
    temp_values=car_Graph.nodes[node]["pos"]
    for keys in MRTDict.keys():
        if haversine(keys[1],keys[0],temp_values[1],temp_values[0])<= 0.015:
            matches[MRTDict[keys]]=node
            break
    if len(matches.keys())==len(MRTDict.values()):
            break
