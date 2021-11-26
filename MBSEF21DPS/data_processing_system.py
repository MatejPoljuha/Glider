import queue
from communication import *
from MBSEF21GUI.MAP_processing import interraction_field_to_obstacle,generate_test_vector_field
import threading
import random
from time import sleep


def run_data_processing_system():
    def simulate_dps_messages(dps_queue: queue.Queue):
        """
        Simulates the glider changing position every 3 seconds, placeholder function - to be replaced when DPS is implemented.
        """
        while True:

            # list_of_random_detected_uplifts=[]
            # for i in range(0,20):
            # ''''simulated uplift in some random position and random strenght. Sternght is send as 0 to 1 value. 0 is minimum, 1 is maximum'''
            # list_of_random_detected_uplifts.append({'x_pos':random.randint(0, 400),'y_pos':random.randint(0, 400),'rel_strength':random.random()})
            #
            while dps_queue.empty():
                sleep(0.2)

            rec = None
            while not dps_queue.empty():
                rec = dps_queue.get()

            vec_field_data = generate_test_vector_field(rec)
            vect_field, coordinates_for_plot, central_points_of_boxes, left_edge_points_of_boxes = vec_field_data
            list_of_detected_uplifts = interraction_field_to_obstacle(vec_field_data)
            # print(list_of_detected_uplifts)
            # not sure if we can have 2 sleeps like this, could cause problems
            """while dps_queue.empty():
                sleep(0.2)"""

            # could cause problems (99% sure it actually will), should NOT be sent along with the other data (aircraft_position, nodes and vector data)
            shortest_path = []
            display_me = []

            # temporary code to not bloat GUI, listens for calculated shortest path to send them to GUI
            while not path_receiving_queue.empty():
                shortest_path = path_receiving_queue.get()
                shortest_path = shortest_path['shortest_path']

                for index, element in enumerate(shortest_path[:-1]):
                    display_me.append((element[0], element[1], shortest_path[index+1][0], shortest_path[index+1][1]))
                print('Path to display: ', display_me)

            temp_dict = {'aircraft_position': [50, 50],
                         'uplift_position': list_of_detected_uplifts,
                         'navigation_line': display_me,
                         'vec_field_data': coordinates_for_plot}
            send_client(destination_port=1501, input_dict=temp_dict, logging=False)

            dict_for_path_planning = {'aircraft_position': [50, 50],
                                      'uplift_position': list_of_detected_uplifts}
            send_client(destination_port=1507, input_dict=dict_for_path_planning, logging=False)

    # renamed these variables to more descriptive names
    weather_receiving_queue = queue.Queue()
    path_receiving_queue = queue.Queue()

    # listens for weather data from weather system (weather streamer)
    listener_weather = threading.Thread(target=receive_server, args=(1505, weather_receiving_queue, False))
    listener_weather.daemon = True
    listener_weather.start()

    # basically runs the dps system
    dps_simulator = threading.Thread(target=simulate_dps_messages, args=(weather_receiving_queue,))
    dps_simulator.daemon = True
    dps_simulator.start()

    # listens for calculated shortest path
    listener_path = threading.Thread(target=receive_server, args=(1508, path_receiving_queue, False))
    listener_path.daemon = True
    listener_path.start()

    # join the threads, maybe needed, maybe not
    listener_weather.join()
    listener_path.join()
    dps_simulator.join()
