from GraphFindingAlgos import minheap


def dijkstra (graph,start,end):
  eco_dict={"Car":118,"Mrt":13,"Bus":73}
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

      edge_weight = edge_data.get('weight', float('inf'))  # Use a default weight if 'length' attribute is missing
      distance = distance_dict[current_node] + edge_weight
      edge_transportation=edge_data.get('transportation','Car')
      if distance < distance_dict[neighbor]:
        distance_dict[neighbor] = distance
        prev_dict[neighbor] = current_node
        heap.insert((neighbor, distance))

  path = []
  current_node = end
  carbon_emission= 0

  while current_node:
    path.append(current_node)
    prev_node = prev_dict[current_node]
    if prev_node:
        transportation_mode = graph.get_edge_data(prev_node, current_node).get('transportation', 'Car')
        distance = graph.get_edge_data(prev_node, current_node).get('weight', 0)
        carbon_emission += distance * eco_dict.get(transportation_mode, 0)
    current_node = prev_dict[current_node]

  path.reverse()
  return (path,round(distance_dict[end],5),carbon_emission)