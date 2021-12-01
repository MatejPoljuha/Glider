import queue
import threading
from itertools import combinations
from math import dist

import networkx as nx
from matplotlib import pyplot as plt

from communication import send_client, receive_server
from time import sleep, time


def run_path_planning():
    # --------------------------------------------------------------------------------------------------------------
    def plan_path():
        starting_position = [0, 0]
        destination_position = [0, 0]
        start_alt = 0
        dest_alt = 0

        node_raw_data = None

        # time in seconds spent at a node, move this out, should be in some sort of simulation module
        time_spent_at_node = 10

        # glide ratio * scaling factor for 100 m
        glide_ratio = 50

        while True:
            weather_update = False
            destination_update = False

            if not incoming_dps_data_queue.empty():
                received_dps_data = incoming_dps_data_queue.get()

                """node_indexes, node_coordinates, node_uplift_data, aircraft_position = [], [], [], []"""

                # starting position, [x,y]
                starting_position = received_dps_data['aircraft_position']

                # raw node data as received from DPS
                node_raw_data = received_dps_data['uplift_position']
                weather_update = True

            if not incoming_gui_data_queue.empty():
                received_gui_data = incoming_gui_data_queue.get()
                destination_position = received_gui_data['destination']

                start_alt = int(received_gui_data['start_altitude'])
                dest_alt = int(received_gui_data['dest_altitude'])
                destination_update = True

            # hack, to stop it from running until it has a destination
            if starting_position != destination_position and (weather_update or destination_update):
                if weather_update:
                    print("WEATHER UPDATED:")
                elif destination_update:
                    print("DESTINATION UPDATED:")
                calculate_plan(node_raw_data,
                               starting_position,
                               destination_position,
                               start_alt,
                               dest_alt,
                               glide_ratio,
                               time_spent_at_node)

            if not weather_update and not destination_update:
                # data will not be updated faster than this so we save some performance with this, queues preserve data that arrives in this window
                sleep(0.2)

    def calculate_plan(node_data, starting_position, destination_position, start_alt, dest_alt, glide_ratio, time_spent_at_node):
        """print('DIJKSTRA INPUT: ')
        print('\nNode data: ', node_data)
        print('\nStarting position: ', starting_position)
        print('\nDestination position: ', destination_position)
        """

        graph = create_graph(node_data, starting_position, destination_position, glide_ratio, start_alt)
        # visualize_graph(graph, graph.nodes(data='coordinates'))

        # band-aid fix, just to remove errors at the start while we have no destination set
        if destination_position != [0, 0]:
            try:
                potential_paths = nx.shortest_simple_paths(graph, 'start', 'dest', weight='weight')

                t3 = time()
                for potential_path in potential_paths:
                    # print(potential_path)
                    if check_path_validity(potential_path, graph, start_alt, dest_alt, glide_ratio, time_spent_at_node):
                        t4 = time()
                        print('Yen: ', potential_path, 'time: ', t4 - t3)
                        display_path = []
                        for node in potential_path:
                            display_path.append(graph.nodes[node]['coordinates'])
                        send_client(1508, input_dict={'shortest_path': display_path}, logging=False)
                        break
            except nx.NetworkXNoPath:
                print('No possible path found!')

    def create_graph(node_list, starting_position, destination_position, glide_ratio, starting_alt):
        # band-aid fix - not optimal, transforms received node data into a better format
        node_list_transformed = {'start': {'coordinates': starting_position},
                                 'dest': {'coordinates': destination_position}}
        for index, node in enumerate(node_list):
            node_list_transformed[str(index)] = {'coordinates': [node['x_pos'], node['y_pos']], 'uplift': node['rel_strength']}

        graph = nx.complete_graph(node_list_transformed, create_using=nx.Graph)
        nx.set_node_attributes(graph, node_list_transformed)

        # adds weights to edges (euclidean distance based on coordinates)
        weighted_edges = []
        for edge in graph.edges:
            edge = list(edge)
            # 1.25 is the scaling factor (to scale down to 100m)
            # real dimensions of map are 64 km x 64 km but it is 512 x 512 pixels
            edge_node_1 = [coordinate for coordinate in graph.nodes(data='coordinates')[edge[0]]]
            edge_node_2 = [coordinate for coordinate in graph.nodes(data='coordinates')[edge[1]]]
            # edge_weight is node distance in meters
            edge_weight = dist(edge_node_1, edge_node_2)
            edge.append(int(edge_weight))
            weighted_edges.append(edge)
        graph.add_weighted_edges_from(weighted_edges)

        kill_unreachable_edges(graph, starting_alt, glide_ratio)

        return graph

    def kill_unreachable_edges(graph, starting_altitude, glide_ratio):
        """
        remove nodes that represent nodes that we cannot reach from the start position
        due to low altitude/large distance
        """
        edges_to_kill = []

        for edge in graph.edges('start', data="weight"):
            if edge[2] // glide_ratio >= starting_altitude:
                edges_to_kill.append((edge[0], edge[1]))
        # print(graph.edges('start'))
        graph.remove_edges_from(edges_to_kill)
        # print('surviving edges: ', graph.edges('start'))

    def check_path_validity(path, graph, start_alt, dist_alt, glide_ratio, time_spent_at_node):
        alt_achieved = start_alt

        for index, node in enumerate(path[1:]):
            travel_loss = graph.get_edge_data(path[index], node)['weight']
            travel_loss /= glide_ratio

            # if glider crashes between nodes
            if travel_loss >= start_alt:
                return False

            # how much time spent at node, multiplies the uplift since it is m/s
            if node != 'dest':
                uplift_gain = graph.nodes[node]['uplift']
                uplift_gain *= time_spent_at_node
                alt_achieved += -travel_loss + uplift_gain
            elif node == 'dest':
                alt_achieved += -travel_loss

        if alt_achieved >= dist_alt:
            return True
        else:
            return False

    def reconstruct_path(came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

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

    incoming_dps_data_queue = queue.Queue()
    incoming_gui_data_queue = queue.Queue()

    # starts server thread that listens for new node positions and aircraft location (starting point for graph)
    dps_server_thread = threading.Thread(target=receive_server, args=(1507, incoming_dps_data_queue, False))
    dps_server_thread.daemon = True
    dps_server_thread.start()

    # starts server thread that listens for input by the user through the GUI, altitudes and destination position
    gui_server_thread = threading.Thread(target=receive_server, args=(1500, incoming_gui_data_queue, False))
    gui_server_thread.daemon = True
    gui_server_thread.start()

    plan_path()

    """# starts client thread that simulates the dps sending node data and current aircraft position
    dps_client_thread = threading.Thread(target=simulate_dps_input, args=())
    dps_client_thread.daemon = True
    dps_client_thread.start()

    # starts client thread that simulates input by the user through the GUI, navigation mode and destination position
    GUI_client_thread = threading.Thread(target=simulate_gui_input, args=())
    GUI_client_thread.daemon = True
    GUI_client_thread.start()"""
