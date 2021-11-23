import requests
import time
import json
import socket
from datetime import datetime
import glob
from communication import receive_server, send_client
import os
from time import sleep


jsonfiles = []
for file in glob.glob("*.json"):
    jsonfiles.append(file)
    

for fil_name in jsonfiles: 
    fil_dir = os.path.dirname(os.path.abspath(__file__))

    json_dict  =None
    with open(fil_dir + '/' +fil_name, "r") as read_file:
        json_dict = json.loads(read_file.read())
        
        
    send_client(destination_port=1505, input_dict=json_dict)
    sleep(5)
    print(json_dict)



#print(txtfiles)    
    



#print(json_received)

#send_client(destination_port=1501, input_dict=dict_list)