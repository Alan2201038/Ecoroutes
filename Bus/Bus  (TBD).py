import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import requests
import itertools

# Define the API endpoints
bus_stops_url = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"
bus_routes_url = "http://datamall2.mytransport.sg/ltaodataservice/BusRoutes"

# Define the headers for the API request
headers = {
    "AccountKey": "nDR1RKXtRtOhzKfgXjcIyQ==",  # replace with your account key
    "accept": "application/json"
}


# Function to handle paginated responses
def fetch_data(url):
    offset = 0
    records = []

    while True:
        response = requests.get(f"{url}?$skip={offset}", headers=headers)
        data = response.json()

        records.extend(data['value'])

        if len(data['value']) < 500:
            break

        offset += 500

    return records


# Fetch data from APIs
bus_stops_data = fetch_data(bus_stops_url)
bus_routes_data = fetch_data(bus_routes_url)

# Convert JSON to pandas DataFrame
bus_stops = pd.json_normalize(bus_stops_data)
bus_routes = pd.json_normalize(bus_routes_data)

bus_stops.set_index('BusStopCode', inplace=True)
bus_routes = bus_routes[bus_routes['BusStopCode'].isin(bus_stops.index)]

transfer_points = bus_routes.groupby('BusStopCode')['ServiceNo'].apply(list).to_dict()

TRANSFER_PENALTY = 0  # artificial cost to discourage unnecessary service changes

G = nx.DiGraph()

# Create a new node for each stop-service pair
for index, stop in bus_routes.iterrows():
    G.add_node((stop['BusStopCode'], stop['ServiceNo']))

# Connect nodes corresponding to consecutive stops on the same service
for service in bus_routes['ServiceNo'].unique():
    service_stops = bus_routes[bus_routes['ServiceNo'] == service].sort_values('StopSequence')
    for (_, stop1), (_, stop2) in zip(service_stops.iterrows(), service_stops.iloc[1:].iterrows()):
        distance = stop2['Distance'] - stop1['Distance']  # Use the difference in the 'Distance' fields
        G.add_edge((stop1['BusStopCode'], service), (stop2['BusStopCode'], service), distance=distance)

# Connect nodes corresponding to the same stop but different services
for stop_code, services in transfer_points.items():
    for service1, service2 in itertools.combinations(services, 2):
        G.add_edge((stop_code, service1), (stop_code, service2), distance=TRANSFER_PENALTY)
        G.add_edge((stop_code, service2), (stop_code, service1), distance=TRANSFER_PENALTY)


def heuristic(node1, node2):
    stop1_code, _ = node1
    stop2_code, _ = node2
    stop1 = bus_stops.loc[stop1_code]
    stop2 = bus_stops.loc[stop2_code]
    stop1_coords = stop1.Latitude, stop1.Longitude
    stop2_coords = stop2.Latitude, stop2.Longitude
    return geodesic(stop1_coords, stop2_coords).km


start_stop = '59079'
end_stop = '59041'

for edge in G.edges(data=True):
    if edge[2]['distance'] < 0:
        print(edge)

start_nodes = [(start_stop, service) for service in transfer_points.get(start_stop, [])]
end_nodes = [(end_stop, service) for service in transfer_points.get(end_stop, [])]

if not start_nodes:
    print(f'Start stop {start_stop} not found in graph.')
elif not end_nodes:
    print(f'End stop {end_stop} not found in graph.')
else:
    # Find the shortest path from any start node to any end node
    paths = []
    for start_node in start_nodes:
        for end_node in end_nodes:
            if nx.has_path(G, start_node, end_node):
                path = nx.astar_path(G, start_node, end_node, heuristic=heuristic)
                total_distance = sum(G.edges[edge]['distance'] for edge in zip(path, path[1:]))
                paths.append((path, total_distance))

    if paths:
        path, total_distance = min(paths, key=lambda x: x[1])  # Get the shortest path
        print("Path found:")
        for (start, service1), (end, service2) in zip(path, path[1:]):
            if start == end:
                print(
                    f'Transfer penalty incurred! Switch from service {service1} to service {service2} at stop {start}')
            else:
                print(f'Take bus service {service1} from stop {start} to stop {end}')

        transfers = len([edge for edge in zip(path, path[1:]) if G.edges[edge]['distance'] == TRANSFER_PENALTY])
        transfer_penalty_exclusion = transfers * TRANSFER_PENALTY
        total_distance = total_distance - transfer_penalty_exclusion
        total_time = total_distance / 30 * 60  # Assuming a speed of 30km/h, convert to minutes
        total_time += transfers * 5  # Add 5 minutes for each transfer
        total_emissions = total_distance * 0.073  # (Source: https://www.eco-business.com/news/singapores-mrt-lines-be-graded-green-ness/)

        print(f'Total distance: {total_distance} km')
        print(f'Total time: {total_time} minutes')
        print(f"Carbon emissions: {total_emissions} kg CO2")

    else:
        print(f'No path found from stop {start_stop} to stop {end_stop}')