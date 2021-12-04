# import requests
import time
import json
import socket
from datetime import datetime
import glob
from communication import receive_server, send_client
import os
from time import sleep
import threading


def run_weather_streamer(weather_refresh_interval, experiment_flag):
    fil_dir = os.path.dirname(os.path.abspath(__file__))

    json_file_list = []

    if experiment_flag == '2':
        print('EXPERIMENT 2')
        for file in glob.glob("{}/weatherFORGED.json".format(fil_dir)):
            json_file_list.append(file)
    if experiment_flag == '1' or experiment_flag == '3':
        print('EXPERIMENT ' + experiment_flag)
        for file in glob.glob("{}/experiment_1_3_scenario.json".format(fil_dir)):
            json_file_list.append(file)
    elif experiment_flag == '0':
        for file in glob.glob("{}/*.json".format(fil_dir)):
            if file != "{}/weatherFORGED.json".format(fil_dir) and file != "{}/weatherSRC.json".format(fil_dir):
                json_file_list.append(file)

    while True:
        for fil_name in json_file_list:

            json_dict = None
            with open(fil_name, "r") as read_file:
                json_dict = json.loads(read_file.read())

            send_client(destination_port=1505, input_dict=json_dict, logging=False)
            sleep(weather_refresh_interval)
