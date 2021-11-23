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
from typing import List, Tuple, TypeVar
import heapq

# 50 means 50m horizontal travel for every 1m of altitude lost
GLIDE_RATIO = 50
T = TypeVar('T')


@dataclass
class Aircraft:
    current_position: tuple = (0, 0, 0)
    glide_ratio: float = GLIDE_RATIO


@dataclass
class GUIInput:
    destination_position: tuple = (0, 0, 0)
    navigation_mode: str = 'fastest'


class PriorityQueue:
    def __init__(self):
        self.elements: List[Tuple[float, T]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


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
    graph_slow = graph
    # graph.remove_edge('1', '7')
    """t1 = time.time()
    print(graph.number_of_edges())
    path = modified_a_star(graph, '1', '180', 200, 400)
    print(graph.number_of_edges())
    t2 = time.time()
    print('Modified A*: ', path, ' Time: ', t2 - t1)"""

    t3 = time.time()
    paths_slow = nx.shortest_simple_paths(graph_slow, '1', '180', weight='weight')
    for path_slow in paths_slow:
        print(path_slow)
        if check_path_validity(path_slow, graph_slow, 200, 400, False):
            break
    t4 = time.time()
    print('Yen: ', path_slow, ' Time: ', t4 - t3)

    # visualize_graph(graph, coordinates)


def modified_a_star(graph, start, goal, alt_budget, goal_alt, remove_1=None, remove_2=None):
    if remove_1 is not None and remove_2 is not None:
        graph.remove_edge(remove_1, remove_2)

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from = {start: None}
    cost_so_far = {start: 0}
    solution = []
    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            potential_solution = reconstruct_path(came_from, start, current)
            if not check_path_validity(potential_solution, graph, alt_budget, goal_alt, True):
                solution = modified_a_star(graph, start, goal, alt_budget, goal_alt, potential_solution[-2], goal)
            else:
                break

        for next_node in graph.neighbors(current):
            edge_weight = graph.get_edge_data(current, next_node)['weight']
            new_cost = cost_so_far[current] + edge_weight

            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + dist(graph.nodes[next_node]['coordinates'], graph.nodes[goal]['coordinates'])
                frontier.put(next_node, priority)
                came_from[next_node] = current
    return solution   # Path not found / not possible


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
        uplift_gain = graph.nodes(data='uplift')[node]
        alt_achieved += travel_loss + uplift_gain

    if alt_achieved >= goal_alt:
        # if astar: print(alt_budget, alt_achieved, goal_alt)
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
