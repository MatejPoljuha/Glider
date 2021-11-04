import socket
import random
from time import sleep
from communication import *


def simulate_dps_input():
    while True:
        temp_dict = {'aircraft_position': [random.randint(0, 400), random.randint(0, 400), random.randint(0, 400)]}
        for i in range(10):
            temp_dict[str(i+1)] = {
                'coordinates': [random.randint(0, 400), random.randint(0, 400)],
                'uplift': random.randint(0, 100),
            }
        send_client(1502, temp_dict, logging=False)
        sleep(8)


def simulate_gui_input():
    while True:
        temp_dict = {
            'navigation_mode': 'fastest',
            'destination_position': [random.randint(0, 400), random.randint(0, 400), random.randint(0, 400)]
        }
        send_client(1503, temp_dict, logging=False)
        sleep(12)
