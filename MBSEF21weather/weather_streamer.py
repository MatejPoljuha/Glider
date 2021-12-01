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


def run_weather_streamer():
    fil_dir = os.path.dirname(os.path.abspath(__file__))

    json_file_list = []
    for file in glob.glob("{}/*.json".format(fil_dir)):
        json_file_list.append(file)
    while(1):
        for fil_name in json_file_list:

            json_dict  =None
            with open(fil_name, "r") as read_file:
                json_dict = json.loads(read_file.read())

            send_client(destination_port=1505, input_dict=json_dict, logging=False)
            sleep(4)
            #print(json_dict)

