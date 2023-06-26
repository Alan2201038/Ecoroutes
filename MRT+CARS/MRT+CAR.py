import os
import pickle
import requests
import matplotlib.pyplot as plt
import networkx as nx
from geopy.geocoders import Nominatim
from GraphFindingAlgos import AStar,Dijkstra
from GraphFindingAlgos import AStar_CarMRT
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

    neighbors = mrt_Graph.neighbors('LABRADOR PARK MRT STATION')

    with open(mrtGraph, "wb") as f:
        pickle.dump(mrt_Graph, f)




matches={'LABRADOR PARK MRT STATION': 10967745984, 'HARBOURFRONT MRT STATION': 10554032491, 'TELOK BLANGAH MRT STATION': 10677661517, 'MARINA SOUTH PIER MRT STATION': 6563309496, 'TUAS CRESCENT MRT STATION': 6198763016, 'GUL CIRCLE MRT STATION': 8386017571, 'TUAS LINK MRT STATION': 8365810407, 'TUAS WEST ROAD MRT STATION': 8374178784, 'JOO KOON MRT STATION': 8651042726, 'PIONEER MRT STATION': 8396102385, 'HAW PAR VILLA MRT STATION': 10708151908, 'PASIR PANJANG MRT STATION': 10859714710, 'KENT RIDGE MRT STATION': 10964931340, 'ONE-NORTH MRT STATION': 7919213957, 'QUEENSTOWN MRT STATION': 10002242948, 'DOVER MRT STATION': 8655132705, 'CLEMENTI MRT STATION': 10899271638, 'BUONA VISTA MRT STATION': 10886417167, 'HOLLAND VILLAGE MRT STATION': 8651604468, 'COMMONWEALTH MRT STATION': 7907705273, 'FARRER ROAD MRT STATION': 10598666071, 'TAN KAH KEE MRT STATION': 9597538682, 'BOON LAY MRT STATION': 6917424293, 'LAKESIDE MRT STATION': 6899717907, 'JURONG EAST MRT STATION': 6770925316, 'CHINESE GARDEN MRT STATION': 8427991048, 'BUKIT BATOK MRT STATION': 10201105002, 'BUKIT GOMBAK MRT STATION': 9754440109, 'KEAT HONG LRT STATION': 8341559798, 'TECK WHYE LRT STATION': 8387395764, 'BEAUTY WORLD MRT STATION': 7929901417, 'KING ALBERT PARK MRT STATION': 10761516901, 'SIXTH AVENUE MRT STATION': 10269634319, 'HUME MRT STATION': 9162290324, 'HILLVIEW MRT STATION': 9162300827, 'CASHEW MRT STATION': 10025875224, 'BUKIT PANJANG MRT STATION': 7795915286, 'PHOENIX LRT STATION': 8359276333, 'PETIR LRT STATION': 9577798173, 'PENDING LRT STATION': 9591217841, 'BANGKIT LRT STATION': 9980315462, 'SOUTH VIEW LRT STATION': 8425495508, 'CHOA CHU KANG MRT STATION': 8650448448, 'YEW TEE MRT STATION': 8419784768, 'SENJA LRT STATION': 8374327926, 'JELAPANG LRT STATION': 9163207788, 'SEGAR LRT STATION': 9381346471, 'FAJAR LRT STATION': 9314479527, 'KRANJI MRT STATION': 6195831617, 'WOODLANDS SOUTH MRT STATION': 9110070766, 'MARSILING MRT STATION': 5256440756, 'WOODLANDS MRT STATION': 10899310588, 'ADMIRALTY MRT STATION': 10126614670, 'WOODLANDS NORTH MRT STATION': 8424382253, 'TIONG BAHRU MRT STATION': 9748614099, 'REDHILL MRT STATION': 10197288433, 'HAVELOCK MRT STATION': 9559583536, 'GREAT WORLD MRT STATION': 10261737210, 'OUTRAM PARK MRT STATION': 9559521769, 'MAXWELL MRT STATION': 10825907486, 'TANJONG PAGAR MRT STATION': 7867196155, 'CHINATOWN MRT STATION': 9742589579, 'TELOK AYER MRT STATION': 6992613959, 'DOWNTOWN MRT STATION': 9497638929, 'SHENTON WAY MRT STATION': 10177596814, 'MARINA BAY MRT STATION': 10000726308, 'RAFFLES PLACE MRT STATION': 6366288503, 'BAYFRONT MRT STATION': 9711156932, 'FORT CANNING MRT STATION': 9717617788, 'CLARKE QUAY MRT STATION': 9855867565, 'SOMERSET MRT STATION': 8685402385, 'DHOBY GHAUT MRT STATION': 8845855291, 'CITY HALL MRT STATION': 9354942758, 'ESPLANADE MRT STATION': 7691071958, 'PROMENADE MRT STATION': 1145428385, 'BRAS BASAH MRT STATION': 9748665319, 'BENCOOLEN MRT STATION': 10885919609, 'BUGIS MRT STATION': 7870619978, 'NAPIER MRT STATION': 10848435238, 'ORCHARD BOULEVARD MRT STATION': 7886371244, 'ORCHARD MRT STATION': 10163766342, 'BOTANIC GARDENS MRT STATION': 8101441023, 'STEVENS MRT STATION': 9559612706, 'NEWTON MRT STATION': 7886543443, 'ROCHOR MRT STATION': 8020948274, 'LITTLE INDIA MRT STATION': 8064241559, 'JALAN BESAR MRT STATION': 10057069139, 'FARRER PARK MRT STATION': 9724057356, 'NOVENA MRT STATION': 2660957661, 'BOON KENG MRT STATION': 10057225981, 'GARDENS BY THE BAY MRT STATION': 8222304088, 'NICOLL HIGHWAY MRT STATION': 6333597582, 'LAVENDER MRT STATION': 8221291499, 'BENDEMEER MRT STATION': 10250805484, 'KALLANG MRT STATION': 8208439470, 'STADIUM MRT STATION': 5184544127, 'MOUNTBATTEN MRT STATION': 8186493104, 'GEYLANG BAHRU MRT STATION': 8655063871, 'ALJUNIED MRT STATION': 6536731012, 'DAKOTA MRT STATION': 9854697276, 'PAYA LEBAR MRT STATION': 6906735175, 'MACPHERSON MRT STATION': 8192467149, 'EUNOS MRT STATION': 10852715572, 'KEMBANGAN MRT STATION': 7682168134, 'TOA PAYOH MRT STATION': 9838930798, 'CALDECOTT MRT STATION': 10907360667, 'BRADDELL MRT STATION': 8073614069, 'MARYMOUNT MRT STATION': 7691088941, 'BISHAN MRT STATION': 6213902791, 'UPPER THOMSON MRT STATION': 10898604744, 'BRIGHT HILL MRT STATION': 9406776048, 'MAYFLOWER MRT STATION': 8882699316, 'ANG MO KIO MRT STATION': 10025784899, 'POTONG PASIR MRT STATION': 10002132047, 'WOODLEIGH MRT STATION': 10793472070, 'MATTAR MRT STATION': 10815584297, 'LORONG CHUAN MRT STATION': 10057068484, 'SERANGOON MRT STATION': 10801813425, 'BARTLEY MRT STATION': 9004247320, 'UBI MRT STATION': 10076606062, 'TAI SENG MRT STATION': 8186414711, 'KAKI BUKIT MRT STATION': 8268824295, 'KOVAN MRT STATION': 8153355277, 'HOUGANG MRT STATION': 8170649184, 'BEDOK MRT STATION': 8982649284, 'TANAH MERAH MRT STATION': 10873214598, 'BEDOK NORTH MRT STATION': 8253734841, 'BEDOK RESERVOIR MRT STATION': 7488022368, 'TAMPINES WEST MRT STATION': 10151494418, 'EXPO MRT STATION': 8298849746, 'SIMEI MRT STATION': 6881927609, 'TAMPINES MRT STATION': 10873314208, 'UPPER CHANGI MRT STATION': 10151364260, 'TAMPINES EAST MRT STATION': 8310129710, 'PASIR RIS MRT STATION': 10855600552, 'CHANGI AIRPORT MRT STATION': 10195306053, 'SPRINGLEAF MRT STATION': 10901446259, 'LENTOR MRT STATION': 10858722365, 'YIO CHU KANG MRT STATION': 6880100027, 'KHATIB MRT STATION': 10057080815, 'YISHUN MRT STATION': 7321012776, 'LAYAR LRT STATION': 8187437221, 'FERNVALE LRT STATION': 8620920513, 'TONGKANG LRT STATION': 8230687501, 'THANGGAM LRT STATION': 10763804492, 'KUPANG LRT STATION': 8229785751, 'BUANGKOK MRT STATION': 10057155140, 'RANGGUNG LRT STATION': 8183331057, 'RENJONG LRT STATION': 8230526171, 'SENGKANG MRT STATION': 9660004037, 'KANGKAR LRT STATION': 8200505603, 'BAKAU LRT STATION': 8236584539, 'RUMBIA LRT STATION': 8272541933, 'FARMWAY LRT STATION': 8686148646, 'CHENG LIM LRT STATION': 6572142183, 'COMPASSVALE LRT STATION': 5928065379, 'SOO TECK LRT STATION': 8189632592, 'COVE LRT STATION': 10065146381, 'CORAL EDGE LRT STATION': 10891356332, 'MERIDIAN LRT STATION': 8277328582, 'PUNGGOL MRT STATION': 10064014553, 'OASIS LRT STATION': 10064048753, 'DAMAI LRT STATION': 8167295980, 'NIBONG LRT STATION': 8935008059, 'SUMANG LRT STATION': 7912426770, 'SAM KEE LRT STATION': 10683626714, 'SAMUDERA LRT STATION': 10132249207, 'PUNGGOL POINT LRT STATION': 8650792591, 'TECK LEE LRT STATION': 10065888364, 'CANBERRA MRT STATION': 10895768470, 'SEMBAWANG MRT STATION': 10685150666, 'RIVIERA LRT STATION': 4713507382, 'KADALOOR LRT STATION': 5218518273}
# MRTDict={}
# matches={}
# for node in mrt_Graph.nodes:
#     temp_values=mrt_Graph.nodes[node]["pos"]
#     shrinked_tuple = tuple(round(value, 7) for value in temp_values)
#     MRTDict[shrinked_tuple]=node
#
# for node in car_Graph.nodes:
#     temp_values=car_Graph.nodes[node]["pos"]
#     for keys in MRTDict.keys():
#         if haversine(keys[1],keys[0],temp_values[1],temp_values[0])<= 0.060:
#             matches[MRTDict[keys]]=node
#             break
#     if len(matches.keys())==len(MRTDict.values()):
#         break
print(matches)
n=car_Graph.neighbors(6213902791)
for i in n:
    print(i)


print("ASD")
for mrt_stns,nodeid in matches.items():
    #print(mrt_stns,nodeid)
    neighbors=mrt_Graph.neighbors(mrt_stns)
    for neighbor in neighbors:
        #print(neighbor)
        edge_data = (mrt_Graph.get_edge_data(mrt_stns, neighbor)['weight']) / 1000
        car_Graph.add_edge(nodeid, matches[neighbor], weight=edge_data,transportation="Mrt")

path,total_distance =AStar_CarMRT(car_Graph, 'WOODLANDS MRT STATION', 'TANJONG PAGAR MRT STATION', 1.2766, 103.8458)