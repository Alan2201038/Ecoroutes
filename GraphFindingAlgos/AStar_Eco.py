import math

from GraphFindingAlgos import minheap
"""This functions calculates the fastest path to the given destination from the given source, it is calculated
using the A* algorithm which uses an additional heuristic in the consideration of the 'best' node to use next"""

def heuristic(time,transport,mode="Eco"):
  eco_dict = {"MRT": 18.05, "bus": 36.5}#Carbon emission per minute
  if mode=="Eco":
    w1=0.88
    w2=0.12
  elif mode=="Balanced":
    w1=0.93
    w2=0.07
  result=w1*time+w2*(time*eco_dict[transport])
  return result

def AStar(graph,start,end,mode="Eco"):
  eco_dict = {"MRT": 18.05, "bus": 36.5}  # Carbon emission per minute

  heap = minheap.MinHeap()
  visited = set()
  time_dict={}
  prev_dict={}
  prev_dict[start]=None
  #time_dict will contain the time taken to get to one place, the type of transportation, eco friendly+time calculation
  for node in graph.nodes:
    if node == start:
      time_dict[node] = (0,"Null",0)
    else:
      time_dict[node] = (float('inf'),"Null",float('inf'))

  #heap will have node no,eco friendly+time calculation,only time
  heap.insert((start,0,0))
  while not heap.check_empty():
    current_node = heap.get_root()[0]

    if current_node == end:  #Reached the target node
      break
    if current_node in visited:
      continue

    visited.add(current_node)

    neighbors = graph.neighbors(current_node)
    for neighbor in neighbors:
      if neighbor in visited:
        continue

      edge_data = graph.get_edge_data(current_node, neighbor)  # Get the edge data between current_node and neighbor
      if 0 in edge_data:
        #mrt edge
        edge_data=edge_data[0]
      else:
        #bus/walk edge
        pass
      edge_weight = edge_data.get('duration', float('inf'))
      edge_transportation=edge_data.get('key','')[:3]
      print(edge_data)
      print(edge_weight)
      print(edge_transportation)

      # total_time = time_dict[current_node][0] + edge_weight
      # neighbour_time=time_dict[neighbor][0]

      total_value=time_dict[current_node][2]+heuristic(edge_weight,edge_transportation,mode)
      neighbor_value=time_dict[neighbor][2]
      if total_value <neighbor_value:
        time_dict[neighbor]=(edge_weight,edge_transportation,total_value)
        prev_dict[neighbor]=current_node
        heap.insert((neighbor,total_value,edge_weight))

  path = []
  current_node = end
  total_carbon=0

  while current_node:
    path.append(current_node)
    curr_time=time_dict[current_node][0]
    curr_transportation=time_dict[current_node][1]
    current_node = prev_dict[current_node]
    if current_node is None:
      break
    curr_time=curr_time-time_dict[current_node][0]
    total_carbon+=curr_time*eco_dict[curr_transportation]


  path.reverse()
  return (path,round(time_dict[end][0],5),total_carbon)