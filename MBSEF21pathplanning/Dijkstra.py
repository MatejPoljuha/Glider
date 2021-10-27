import networkx as nx
import numpy as np

#input nodes, edges and weight
nodes = [0,1,2,3,4,5]
edges = [(0,1,1),(0,2,1),(1,2,1),(2,4,1),(1,3,1),(1,4,1),(3,5,1),(3,4,1),(4,5,1)]
n_edge, n_node = len(edges), len(nodes)

#construct the graph using networkx
Graph = nx.DiFraph()
Graph.add_nodes_from(nodes)
Graph.add_weighted_edges_from(edges)

#initialization
start_node = 0
temp_label_node, optimal_label_node = nodes, []
distance = np.array([0 if n == start_node else np.Infinity for n in nodes])
shortest_path_tree = [start_node for n in nodes]

#update label
while len(temp_label_node) > 0:
    i = temp_label_node[np.argmin(distance[temp_label_node])]
    optimal_label_node.append(i)
    temp_label_node.remove(i)
    for j in list(Graph.neighbors(i)):
        if distance[j] > distance[i] + Graph[i][j]['weight']:
            distance[j] = distance[i] + Graph[i][j]['weight']
            shortest_path_tree[j] = i
print(distance)
print(shortest_path_tree)
