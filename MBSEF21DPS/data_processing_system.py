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


            '''simulates path based on node positions - normally provided by Matej'''
            navigation_line_sim = []

            temp_dict = {'aircraft_position': [50, 50],
                         'uplift_position': list_of_detected_uplifts, 'navigation_line': navigation_line_sim,'vec_field_data': coordinates_for_plot}
            send_client(destination_port=1501, input_dict=temp_dict)
            dict_for_pathplanning= {'aircraft_position': [50, 50],
                         'uplift_position': list_of_detected_uplifts}
            send_client(destination_port=1507, input_dict=dict_for_pathplanning)

    receiving_queue = queue.Queue()

    y = threading.Thread(target=receive_server, args=(1505, receiving_queue, True))
    y.daemon = True
    y.start()

    z = threading.Thread(target=simulate_dps_messages, args=(receiving_queue,))
    z.daemon = True
    z.start()

    z.join()
    y.join()
