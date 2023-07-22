from GraphFindingAlgos import minheap


def dijkstra (graph,start,end):
  co2 = 118

  heap = minheap.MinHeap()
  visited = set()
  distance_dict={}#Keeps track of the current shortest distance of all vertices from the start node
  prev_dict={}#Keeps track of the shortest previous node
  prev_dict[start]=None
  for node in graph.nodes:
    if node == start:
      distance_dict[node] = 0
    else:
      distance_dict[node] = float('inf')


  heap.insert((start, 0))
  while not heap.check_empty():
    current_node, current_distance = heap.get_root()

    if current_node == end:  # dest
      break
    if current_node in visited:
      continue

    visited.add(current_node)

    neighbors = graph.neighbors(current_node)
    for neighbor in neighbors:
      edge_data = graph.get_edge_data(current_node, neighbor)  # Get the edge data between current_node and neighbor
      if not edge_data:
        continue
      edge_data=edge_data[0]
      edge_weight = edge_data.get('length', float('inf'))  # Use a default weight if 'length' attribute is missing
      distance = distance_dict[current_node] + edge_weight
      if distance < distance_dict[neighbor]:
        distance_dict[neighbor] = distance
        prev_dict[neighbor] = current_node
        heap.insert((neighbor, distance))

  path = []
  current_node = end
  total_carbon=0

  while current_node:
    path.append(current_node)
    curr_dist = distance_dict[current_node]
    current_node = prev_dict[current_node]
    if current_node is None:
      break
    curr_dist = curr_dist - distance_dict[current_node]
    total_carbon += curr_dist * co2

  path.reverse()
  return (path,round(distance_dict[end],5
                     )/1000,total_carbon/1000)