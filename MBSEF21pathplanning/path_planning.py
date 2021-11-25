import threading
import time
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence
from math import dist

import networkx as nx
from matplotlib import pyplot as plt

from communication import receive_server
from dps_simulator import *


# 50 means 50m horizontal travel for every 1m of altitude lost
GLIDE_RATIO = 50


@dataclass
class Aircraft:
    current_position: tuple = (0, 0, 0)
    glide_ratio: float = GLIDE_RATIO


@dataclass
class GUIInput:
    destination_position: Sequence = (0, 0, 0)
    navigation_mode: str = 'fastest'


def main():
    plan_path()


# --------------------------------------------------------------------------------------------------------------
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

            gui_data = GUIInput((0, 0, 0))

            if not incoming_gui_data_queue.empty():
                received_gui_data = incoming_gui_data_queue.get()
                gui_data = GUIInput(destination_position=received_gui_data['destination_position'],
                                    navigation_mode=received_gui_data['navigation_mode'])

            calculate_plan(received_dps_data,
                           aircraft.current_position,
                           gui_data.destination_position,
                           gui_data.navigation_mode)


def create_graph(node_list, starting_position, destination_position, starting_alt=0, destination_alt=0):
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

    # remove nodes that represent nodes that we cannot reach from the start position due to low altitude/large distance
    kill_unreachable_edges(graph, starting_position, 2)

    return graph


def kill_unreachable_edges(graph, starting_position, starting_altitude):
    edges_to_kill = []
    for edge in graph.edges(starting_position, data="weight"):
        if edge[2]/GLIDE_RATIO >= starting_altitude:
            # print('Crash because starting alt: ', starting_altitude, ' but alt loss: ', edge[2]/GLIDE_RATIO)
            edges_to_kill.append((edge[0], edge[1]))
    graph.remove_edges_from(edges_to_kill)
    print(graph.edges(starting_position))


def calculate_plan(node_data, starting_position, destination_position, navigation_mode):
    """print('DIJKSTRA INPUT: ')
    print('\nNode data: ', node_data)
    print('\nStarting position: ', starting_position)
    print('\nDestination position: ', destination_position)
    print('\nNavigation mode: ', navigation_mode)"""

    graph = create_graph(node_data, '1', destination_position)
    graph_slow = graph

    paths_slow = nx.shortest_simple_paths(graph_slow, '1', '180', weight='weight')

    t3 = time.time()
    for path_slow in paths_slow:
        if check_path_validity(path_slow, graph_slow, 200, 400, False):
            t4 = time.time()
            print('Yen: ', path_slow, 'time: ', t4 - t3)
            break

    # visualize_graph(graph, coordinates)


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def check_path_validity(path, graph, alt_budget, goal_alt, astar):
    alt_achieved = alt_budget

    for index, node in enumerate(path[1:]):
        travel_loss = graph.get_edge_data(path[index], node)['weight']
        travel_loss /= GLIDE_RATIO

        # if glider crashes between nodes
        if travel_loss >= alt_budget:
            return False

        uplift_gain = graph.nodes(data='uplift')[node]
        alt_achieved += travel_loss + uplift_gain
    if alt_achieved >= goal_alt:
        return True
    else:
        return False


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
