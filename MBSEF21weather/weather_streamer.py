import requests
import time
import json
import socket
from datetime import datetime
from communication import *


with open("weather.json", "r") as read_file:
    json_received = json.loads(read_file.read())


print(json_received)

#send_client(destination_port=1501, input_dict=dict_list)