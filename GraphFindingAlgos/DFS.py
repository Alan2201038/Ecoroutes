import math

def depth_first_Search_route(graph, start, end):
    stack = [(start, [start])]
    visited = set()
    total_distance = 0
    eco_dict={"Car":118,"Mrt":13,"Bus":73}
    total_emission = 0

    while stack:
        node, path = stack.pop()

        if node == end:
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]

                current_pos = graph.nodes[current_node]['pos'][:2]
                next_pos = graph.nodes[next_node]['pos'][:2]

                distance = calculate_distance(current_pos[0], current_pos[1], next_pos[0], next_pos[1])
                total_distance += distance

                # Calculate emission based on the transportation mode
                transportation_mode = graph.get_edge_data(current_node, next_node, default={}).get('transportation', 'Car')
                if transportation_mode in eco_dict:
                    emission = eco_dict[transportation_mode]
                    total_emission += emission * distance

            return path, total_distance,total_emission

        if node in visited:
            continue

        visited.add(node)

        if node not in graph.nodes:
            continue

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))
    
    return None

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


