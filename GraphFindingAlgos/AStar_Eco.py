import math

from GraphFindingAlgos import minheap
"""This functions calculates the fastest path to the given destination from the given source, it is calculated
using the A* algorithm which uses an additional heuristic in the consideration of the 'best' node to use next"""

def heuristic(lon1, lat1, lon2, lat2):
  #Haversine used as the heuristic
  radius = 6371
  lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  distance = radius * c

  return distance

def AStar(graph,start,end,end_lat,end_lon,mode="Eco"):
  if mode=="Eco":
    w1=0.88
    w2=0.12
  else:
    w1=0.93
    w2=0.07
  eco_dict={"Car":118,"Mrt":13,"Bus":73}

  heap = minheap.MinHeap()
  visited = set()
  distance_dict={}#Keeps track of the shortest path of vertex from the start node,heuristic cost and type of transport
  prev_dict={}#Keeps track of the shortest previous node
  prev_dict[start]=None
  for node in graph.nodes:
    if node == start:
      distance_dict[node] = (0,0,"Null")
    else:
      distance_dict[node] = (float('inf'),float('inf'),"Null")


  heap.insert((start, 0,0))
  while not heap.check_empty():
    current_node, current_distance,est_dist = heap.get_root()

    if current_node == end:  #Reached the target node
      break
    if current_node in visited:
      continue

    visited.add(current_node)

    neighbors = graph.neighbors(current_node)
    for neighbor in neighbors:
      edge_data = graph.get_edge_data(current_node, neighbor)  # Get the edge data between current_node and neighbor
      edge_weight = edge_data.get('weight', float('inf'))
      edge_direction = edge_data.get('direction', 'both')  # Get the direction attribute of the edge
      edge_transportation=edge_data.get('transportation','Car')
      if edge_direction == 'backward':
        # Illegal route since it's a one-way street, so ignore
        continue

      node_data = graph.nodes[neighbor]["pos"]
      latitude,longitude=node_data[0],node_data[1]

      heu = heuristic(longitude, latitude, end_lon, end_lat)
      total_distance = distance_dict[current_node][0] + edge_weight + heu
      neighbour_distance=distance_dict[neighbor][0]+distance_dict[neighbor][1]
      eco_total_distance=w1*(total_distance)+w2*eco_dict[edge_transportation]
      eco_neighbour_distance=w1*(neighbour_distance)+w2*eco_dict.get(distance_dict[neighbor][2],1)

      # Check if the total distance travelled is less than actual distance + heuristic of the neighbour node
      if eco_total_distance < eco_neighbour_distance:
        distance_dict[neighbor] = (total_distance - heu, heu,edge_transportation)
        prev_dict[neighbor] = current_node
        heap.insert((neighbor, total_distance, heu))

  path = []
  current_node = end
  total_carbon=0

  while current_node:
    path.append(current_node)
    curr_dist=distance_dict[current_node][0]
    curr_transportation=distance_dict[current_node][2]
    current_node = prev_dict[current_node]
    if current_node is None:
      break
    curr_dist=curr_dist-distance_dict[current_node][0]
    total_carbon+=curr_dist*eco_dict[curr_transportation]


  path.reverse()
  return (path,round(distance_dict[end][0],5),total_carbon)