
import math

from Cars.GraphFindingAlgos import minheap

def heuristic(lat1,lon1,lat2,lon2):
  #Uses Euclidean distance as the heuristic
  lat1 = math.radians(lat1)
  lon1 = math.radians(lon1)
  lat2 = math.radians(lat2)
  lon2 = math.radians(lon2)

  d = math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
  return d

def AStar(graph,start,end,end_lon,end_lat):

  heap = minheap.MinHeap()
  visited = set()
  distance_dict={}#Keeps track of the current shortest distance of all vertices from the start node and estimated dist to end node
  prev_dict={}#Keeps track of the shortest previous node
  prev_dict[start]=None
  for node in graph.nodes:
    if node == start:
      distance_dict[node] = (0,0)
    else:
      distance_dict[node] = float('inf')


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
      distance = distance_dict[current_node] + edge_weight
      if distance < distance_dict[neighbor]:
        distance_dict[neighbor] = distance
        prev_dict[neighbor] = current_node
        heap.insert((neighbor, distance))

  path = []
  current_node = end

  while current_node:
    path.append(current_node)
    current_node = prev_dict[current_node]

  path.reverse()
  return (path,round(distance_dict[end],5))