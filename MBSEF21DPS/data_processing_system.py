import queue
from communication import *
from MBSEF21GUI.MAP_processing import interraction_field_to_obstacle,generate_test_vector_field
import threading
import random
from time import sleep


def simulate_dps_messages():
    """
    Simulates the glider changing position every 3 seconds, placeholder function - to be replaced when DPS is implemented.
    """
    global data_queue
    while True:

        # list_of_random_detected_uplifts=[]
        # for i in range(0,20):
        # ''''simulated uplift in some random position and random strenght. Sternght is send as 0 to 1 value. 0 is minimum, 1 is maximum'''
        # list_of_random_detected_uplifts.append({'x_pos':random.randint(0, 400),'y_pos':random.randint(0, 400),'rel_strength':random.random()})
        #
        while data_queue.empty():
            sleep(0.2)
            
        rec = None
        while not data_queue.empty():
            rec = data_queue.get()
            
        vec_field_data = generate_test_vector_field(rec)
        list_of_detected_uplifts = interraction_field_to_obstacle(vec_field_data)
        

        '''simulates path based on node positions - normally provided by Matej'''
        navigation_line_sim = []

        start_index = random.randint(0, 20)
        old_x = list_of_detected_uplifts[0 + start_index]['x_pos']
        old_y = list_of_detected_uplifts[0 + start_index]['y_pos']
        for i in range(1 + start_index, 15 + start_index):
            new_x = list_of_detected_uplifts[i]['x_pos']
            new_y = list_of_detected_uplifts[i]['y_pos']
            navigation_line_sim.append((old_x, old_y, new_x, new_y))
            old_x = new_x
            old_y = new_y
            
            
        temp_dict = {'aircraft_position': [random.randint(0, 400), random.randint(0, 400)],
                     'uplift_position': list_of_detected_uplifts, 'navigation_line': navigation_line_sim, 'vec_field_data': vec_field_data}
        send_client(destination_port=1501, input_dict=temp_dict)
        sleep(3.0)

data_queue = queue.Queue()

y = threading.Thread(target=receive_server, args=(1505, data_queue, True))
y.daemon = True
y.start()

z = threading.Thread(target=simulate_dps_messages, args=())
z.daemon = True
z.start()

z.join()
y.join()
