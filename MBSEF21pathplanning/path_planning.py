from matplotlib import pyplot as plt
from itertools import combinations, islice, count
import heapq as hp
import networkx as nx
import threading
import socket
import random
import time
from time import sleep
import numpy as np
import base64
import queue
from dataclasses import dataclass, field
from dps_simulator import *
from communication import send_client, receive_server
from math import dist
from typing import List

# 50 means 50m horizontal travel for every 1m of altitude lost
GLIDE_RATIO = 50


@dataclass
class Aircraft:
    current_position: tuple = (0, 0, 0)
    glide_ratio: float = GLIDE_RATIO


@dataclass
class GUIInput:
    destination_position: tuple = (0, 0, 0)
    navigation_mode: str = 'fastest'


def main():
    plan_path()


# -------------------------------------------------- RECEIVING DATA --------------------------------------------------
def plan_path():
    while True:
        while not incoming_dps_data_queue.empty():
            received_dps_data = incoming_dps_data_queue.get()

            """node_indexes, node_coordinates, node_uplift_data, aircraft_position = [], [], [], []"""

            aircraft = Aircraft(current_position=received_dps_data['aircraft_position'])
            received_dps_data.pop('aircraft_position')

            """for key in received_dps_data:
                node_indexes.append(key)
                node_coordinates.append(received_dps_data[key]['coordinates'])
                node_uplift_data.append(received_dps_data[key]['uplift'])

            print('Node indexes: ', node_indexes)
            print('Node coordinates: ', node_coordinates)
            print('Node uplift data: ', node_uplift_data)"""

            gui_data = GUIInput([0, 0, 0])

            if not incoming_gui_data_queue.empty():
                received_gui_data = incoming_gui_data_queue.get()
                gui_data = GUIInput(destination_position=received_gui_data['destination_position'],
                                    navigation_mode=received_gui_data['navigation_mode'])

            calculate_plan(received_dps_data,
                           aircraft.current_position,
                           gui_data.destination_position,
                           gui_data.navigation_mode)


def create_graph(node_list, starting_position, destination_position):
    graph = nx.Graph()

    # creates graph nodes
    graph.add_nodes_from(node_list)
    nx.set_node_attributes(graph, node_list)

    # creates graph edges
    edges = combinations(node_list, 2)

    # adds weights to edges (euclidean distance based on coordinates)
    weighted_edges = []
    for edge in edges:
        edge = list(edge)
        edge.append(dist(graph.nodes(data='coordinates')[edge[0]],
                         graph.nodes(data='coordinates')[edge[1]]))
        weighted_edges.append(edge)
    graph.add_weighted_edges_from(weighted_edges)

    return graph


def calculate_plan(node_data, starting_position, destination_position, navigation_mode):
    """print('DIJKSTRA INPUT: ')
    print('\nNode data: ', node_data)
    print('\nStarting position: ', starting_position)
    print('\nDestination position: ', destination_position)
    print('\nNavigation mode: ', navigation_mode)"""

    graph = create_graph(node_data, starting_position, destination_position)

    coordinates = nx.get_node_attributes(graph, 'coordinates')
    uplift = nx.get_node_attributes(graph, 'uplift')

    """t1 = time.time()
    path = astar(graph, '1', '180')
    t2 = time.time()
    print(path, t2-t1)"""

    t1 = time.time()
    paths = nx.shortest_simple_paths(graph, '1', '180', weight='weight')
    t2 = time.time()

    """for path in paths:
        print(path)"""

    print('All: ', t2-t1, 'seconds')

    t3 = time.time()
    paths = islice(nx.shortest_simple_paths(graph, '1', '180', weight='weight'), 10)
    t4 = time.time()
    print('First 10: ', t4-t3, 'seconds')




    for path in paths:
        print(path)
    print('-----------------------')
    # visualize_graph(graph, coordinates)


def astar(G, source, target, heuristic=None, weight="weight"):
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
        def heuristic(u, v):
            return 0

    push = hp.heappush
    pop = hp.heappop
    weight = nx.shortest_paths.weighted._weight_function(G, weight)

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    c = count()
    queue = [(0, next(c), source, 0, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = pop(queue)

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost, h = enqueued[curnode]
            if qcost < dist:
                continue

        explored[curnode] = parent

        for neighbor, w in G[curnode].items():
            ncost = dist + weight(curnode, neighbor, w)
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                # if qcost <= ncost, a less costly path from the
                # neighbor to the source was already determined.
                # Therefore, we won't attempt to push this neighbor
                # to the queue
                if qcost <= ncost:
                    continue
            else:
                h = heuristic(neighbor, target)
            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")



def visualize_graph(g, node_positions):
    plt.figure(figsize=(5, 5), dpi=200, frameon=False)
    plt.axis('equal')
    nx.draw_networkx(
        g,
        node_positions,
        arrows=False,
        with_labels=True,
        node_size=9,
        node_color='#3399ff',
        edge_color='#808080',
        font_size=10,
        font_color='#000000',
        verticalalignment='bottom',
        horizontalalignment='center'
    )
    plt.show()


if __name__ == '__main__':
    # -------------------------------------------------- THREADS --------------------------------------------------
    incoming_dps_data_queue = queue.Queue()
    incoming_gui_data_queue = queue.Queue()

    # starts server thread that listens for new node positions and aircraft location (starting point for graph)
    dps_server_thread = threading.Thread(target=receive_server, args=(1502, incoming_dps_data_queue, False))
    dps_server_thread.daemon = True
    dps_server_thread.start()

    # starts server thread that listens for input by the user through the GUI, navigation mode and destination position
    GUI_server_thread = threading.Thread(target=receive_server, args=(1503, incoming_gui_data_queue, False))
    GUI_server_thread.daemon = True
    GUI_server_thread.start()

    # just so the first connection doesn't get refused
    sleep(2)

    # starts client thread that simulates the dps sending node data and current aircraft position
    dps_client_thread = threading.Thread(target=simulate_dps_input, args=())
    dps_client_thread.daemon = True
    dps_client_thread.start()

    # starts client thread that simulates input by the user through the GUI, navigation mode and destination position
    GUI_client_thread = threading.Thread(target=simulate_gui_input, args=())
    GUI_client_thread.daemon = True
    GUI_client_thread.start()

    # -------------------------------------------------- MAIN --------------------------------------------------
    main()
