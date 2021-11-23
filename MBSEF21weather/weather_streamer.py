import requests
import time
import json
import socket
from datetime import datetime



with open("weather.json", "w") as write_file:
    json.dump(dict_list, write_file)

send_client(destination_port=1501, input_dict=dict_list)