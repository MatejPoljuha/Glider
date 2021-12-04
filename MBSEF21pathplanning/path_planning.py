import queue
import threading
import logging
import networkx as nx
from math import dist
from matplotlib import pyplot as plt
from datetime import datetime
from communication import send_client, receive_server
from time import sleep, time


def run_path_planning(weather_refresh_interval, time_spent_at_node):
    def calculate_plan(graph, start_alt, dest_alt, glide_ratio, time_spent_at_node, last_weather_update):
        timed_out = False
        # starts timing execution of algorithm
        algorithm_start_time = time()

        try:
            potential_paths = nx.shortest_simple_paths(graph, 'start', 'dest', weight='weight')
            for potential_path in potential_paths:
                algorithm_taken_time = time() - algorithm_start_time
                # if the algorithm takes more than a reasonable amount of time to find a solution, stop it and say there is no path
                if algorithm_taken_time > min(weather_refresh_interval / 0.66, weather_refresh_interval - float(time() - last_weather_update) - 0.1, 10):
                    timed_out = True
                    raise nx.NetworkXNoPath

                if check_path_validity(potential_path, graph, start_alt, dest_alt, glide_ratio, time_spent_at_node):
                    # converts path into display format and sends it to GUI
                    send_path_to_gui(potential_path)

                    path_length, altitudes = get_shortest_path_info(potential_path, start_alt)

                    return potential_path, algorithm_taken_time, path_length, altitudes
        except (nx.NetworkXNoPath, nx.NetworkXError):
            algorithm_taken_time = time() - algorithm_start_time
            if timed_out:
                return 'Timed out', algorithm_taken_time, 0, '-'
            else:
                return 'No path found', algorithm_taken_time, 0, '-'
        return 'No path found', algorithm_taken_time, 0, '-'

    def create_graph(node_list, starting_position, destination_position, glide_ratio, starting_alt):
        node_list_transformed = {'start': {'coordinates': starting_position},
                                 'dest': {'coordinates': destination_position}}

        for index, node in enumerate(node_list):
            coordinates = [node['x_pos'], node['y_pos']]
            start_coordinates = node_list_transformed['start']['coordinates']
            dest_coordinates = node_list_transformed['dest']['coordinates']

            # if start/destination are uplift zones, skips them, otherwise reformat the input data into this dict form
            if coordinates != start_coordinates and coordinates != dest_coordinates:
                node_list_transformed[str(index + 1)] = {'coordinates': coordinates,
                                                         'uplift': node['rel_strength']}

        graph = nx.complete_graph(node_list_transformed, create_using=nx.Graph)
        nx.set_node_attributes(graph, node_list_transformed)

        # adds weights to edges (euclidean distance based on coordinates)
        weighted_edges = []

        for edge in graph.edges:
            edge = list(edge)
            # real dimensions of map are 64 km x 64 km but it is 512 x 512 pixels so a scaling factor is needed
            edge_node_1 = [coordinate * 125 for coordinate in graph.nodes(data='coordinates')[edge[0]]]
            edge_node_2 = [coordinate * 125 for coordinate in graph.nodes(data='coordinates')[edge[1]]]

            # edge_weight is node distance in meters
            edge_weight = dist(edge_node_1, edge_node_2)
            edge.append(int(edge_weight))
            weighted_edges.append(edge)
        graph.add_weighted_edges_from(weighted_edges)

        kill_unreachable_edges(graph, starting_alt, glide_ratio)

        return graph

    def kill_unreachable_edges(graph, starting_altitude, glide_ratio):
        """
        removes edges that the glider cannot reach from the start position
        due to low altitude/large distance and edges that are impossible to reach even if we visit every single uplift point
        """
        edges_to_kill = []

        # finds edges that are unreachable from the start
        for edge in graph.edges('start', data="weight"):
            if edge[2] // glide_ratio >= starting_altitude:
                edges_to_kill.append((edge[0], edge[1]))

        # finds edges that are unreachable even with maximum uplift
        max_achieved_alt = starting_altitude
        for node in graph.nodes(data=True):
            if node[0] != 'start' and node[0] != 'dest':
                # 4000 meters it the maximum safe altitude for gliding
                max_achieved_alt = min(4000, max_achieved_alt + node[1]['uplift']*time_spent_at_node)

        for edge in graph.edges(data="weight"):
            if edge[2] // glide_ratio > max_achieved_alt:
                edges_to_kill.append((edge[0], edge[1]))

        graph.remove_edges_from(edges_to_kill)

    def check_path_validity(path, graph, start_alt, dist_alt, glide_ratio, time_spent_at_node):
        """
        checks if a path is possible within the altitude constraints
        """
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
                # 4000 meters it the maximum safe altitude for gliding so if the path necessitates it, we assume the pilot would stop themselves before exceeding it
                alt_achieved = min(4000, alt_achieved + uplift_gain - travel_loss)
            elif node == 'dest':
                alt_achieved += -travel_loss

        if alt_achieved >= dist_alt:
            return True
        else:
            return False

    def get_shortest_path_info(path, starting_altitude):
        """
        Goes through the calculated path and retrieves info about it from the graph structure
        """
        path_length = 0
        altitudes = [starting_altitude]
        current_altitude = starting_altitude

        for index, node in enumerate(path[1:]):
            node_distance = graph.get_edge_data(path[index], node)['weight']
            path_length += node_distance
            if node != 'dest':
                current_altitude += graph.nodes[node]['uplift'] * time_spent_at_node - node_distance / glide_ratio
            elif node == 'dest':
                current_altitude -= node_distance / glide_ratio
            altitudes.append(int(current_altitude))

        return path_length, altitudes

    def send_path_to_gui(potential_path):
        """
        Sends the path to GUI in a different format.
        """
        display_path = []
        for node in potential_path:
            display_path.append(graph.nodes[node]['coordinates'])
        send_client(1508, input_dict={'shortest_path': display_path}, logging=False)

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

    logging.basicConfig(filename="results.log", filemode='w', level=logging.INFO, format='%(message)s')

    column_names = " {:^17} | {:^27} | {:^11} | {:^24} | {:^27} | {:^33} | {:^20} | {:^24} | {:^30}".format(
        'algorithm_run_ID',
        'run_reason',
        'timestamp',
        'algorithm_run_time [s]',
        'start coordinates [x,y,z]',
        'destination coordinates [x,y,z]',
        'length_of_path [m]',
        'time_spent_at_node [s]',
        'weather_refresh_interval [s]')
    logging.info(column_names + ' | shortest_path found' + ' | altitude_changes [m]')

    # starts server thread that listens for new node positions and aircraft location (starting point for graph)
    incoming_dps_data_queue = queue.Queue()
    dps_server_thread = threading.Thread(target=receive_server, args=(1507, incoming_dps_data_queue, False))
    dps_server_thread.daemon = True
    dps_server_thread.start()

    # starts server thread that listens for input by the user through the GUI, altitudes and destination position
    incoming_gui_data_queue = queue.Queue()
    gui_server_thread = threading.Thread(target=receive_server, args=(1500, incoming_gui_data_queue, False))
    gui_server_thread.daemon = True
    gui_server_thread.start()

    # default values
    starting_position = [0, 0]
    destination_position = [0, 0]
    start_alt = 0
    dest_alt = 0

    node_raw_data = None

    # time in seconds spent at a node, move this out, should be in some sort of simulation module
    # time_spent_at_node = 180

    # glide ratio * scaling factor for 100 m
    glide_ratio = 50

    # default log values
    run_results = ''

    run_counter = 0
    run_reason = ''
    algorithm_run_time = 0
    length_of_path = 0
    altitude_changes = []

    # weather_refresh_interval = 1
    last_weather_update = time()

    while True:
        weather_update = False
        destination_update = False

        if not incoming_dps_data_queue.empty():
            received_dps_data = incoming_dps_data_queue.get()

            """node_indexes, node_coordinates, node_uplift_data, aircraft_position = [], [], [], []"""

            # starting position, [x,y]
            # starting_position = received_dps_data['aircraft_position']

            # raw node data as received from DPS
            node_raw_data = received_dps_data['uplift_position']
            weather_update = True
            last_weather_update = time()

        if not incoming_gui_data_queue.empty():
            received_gui_data = incoming_gui_data_queue.get()
            destination_position = received_gui_data['destination']

            start_alt = int(received_gui_data['start_altitude'])
            dest_alt = int(received_gui_data['dest_altitude'])
            # received from GUI for purposes of simulation but in reality would be from DPS
            starting_position = received_gui_data['starting_position']
            # weather_refresh_interval = received_gui_data['weather_refresh_interval']
            destination_update = True

        if destination_position != [0, 0] and (weather_update or destination_update):
            run_counter += 1

            if weather_update or destination_update:
                if weather_update and destination_update:
                    run_reason = 'weather + new destination'
                elif weather_update:
                    run_reason = 'weather'
                elif destination_update:
                    run_reason = 'new destination'

            # creates graph structure as networkx complete undirected weighted graph
            graph = create_graph(node_raw_data, starting_position, destination_position, glide_ratio, start_alt)
            print(graph.edges('dest'))
            # visualize_graph(graph, graph.nodes(data='coordinates'))

            shortest_path, algorithm_run_time, shortest_path_length, altitude_changes = calculate_plan(graph,
                                                                                                       start_alt,
                                                                                                       dest_alt,
                                                                                                       glide_ratio,
                                                                                                       time_spent_at_node,
                                                                                                       last_weather_update)

            run_results = " {:^17} | {:^27} | {:^11} | {:^24} | {:^27} | {:^33} | {:^20} | {:^24} | {:^30}".format(
                run_counter,
                run_reason,
                datetime.now().strftime("%H:%M:%S"),
                round(algorithm_run_time, 4),
                str([starting_position[0], starting_position[1], start_alt]),
                str([destination_position[0], destination_position[1], dest_alt]),
                shortest_path_length,
                time_spent_at_node,
                weather_refresh_interval
            )
            logging.info(run_results + ' | ' + str(shortest_path) + ' | ' + str(altitude_changes))

        if not weather_update and not destination_update:
            # data will not be updated faster than this so we save some performance with this, queues preserve data that arrives during this window
            sleep(0.1)
