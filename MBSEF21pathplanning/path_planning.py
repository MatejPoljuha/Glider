from MBSEF21GUI.GUI_networking import *
from matplotlib import pyplot as plt
from itertools import combinations
from io import BytesIO
import networkx as nx
import threading
import socket
import random
from time import sleep
import numpy as np
import base64
import queue
from dataclasses import dataclass, field
from dps_simulator import *
from communication import *
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
    destination_position: list
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


def calculate_plan(node_data, starting_position, destination_position, navigation_mode):
    print('DIJKSTRA INPUT: ')
    print('\nNode data: ', node_data)
    print('\nStarting position: ', starting_position)
    print('\nDestination position: ', destination_position)
    print('\nNavigation mode: ', navigation_mode)

    graph = create_graph(node_data, create_edges_test())

    coordinates = nx.get_node_attributes(graph, 'coordinates')
    uplift = nx.get_node_attributes(graph, 'uplift')

    visualize_graph(graph, coordinates)


def create_graph(node_list, edge_list):
    graph = nx.Graph()
    graph.add_nodes_from(node_list)
    nx.set_node_attributes(graph, node_list)
    graph.add_weighted_edges_from(edge_list)

    return graph


def create_edges_test():
    # return combinations(node_list, 2)
    return [('2', '1', 1.1),
            ('8', '3', 1.0),
            ('1', '3', 4.2),
            ('1', '2', 1.2),
            ('2', '5', 2.3),
            ('3', '4', 1.0),
            ('5', '4', 2.1),
            ('2', '6', 3.3)]


def create_edges(node_list):
    pass


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


"""
def flight_mode_cost_function(src, dest, edge_attributes):
    weight = edge_attributes.get("weight", 1) * random.randint(1, 30)
    print(weight)
    return weight
"""
