
# shortest_path=nx.shortest_path(graph, node_source, node_target, weight='length')
# shortest_distance=nx.shortest_path_length(graph, node_source, node_target, weight='length')
# print(shortest_path)
# print(shortest_distance)
# ASTAR=AStar_Car.AStar(graph,node_source,node_target)
# print(ASTAR)
asd_path=Dijkstra.dijkstra(graph,node_source,node_target)
print(asd_path)