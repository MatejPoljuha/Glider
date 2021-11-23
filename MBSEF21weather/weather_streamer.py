import requests
import time
import json
import socket
from datetime import datetime
import glob
from communication import receive_server, send_client
import os
from time import sleep

fil_dir = os.path.dirname(os.path.abspath(__file__))

jsonfiles = []
for file in glob.glob("{}/*.json".format(fil_dir)):
    jsonfiles.append(file)


while(1):
    for fil_name in jsonfiles: 
        
    
        json_dict  =None
        with open(fil_name, "r") as read_file:
            json_dict = json.loads(read_file.read())
            
            
        send_client(destination_port=1505, input_dict=json_dict)
        sleep(3)
        #print(json_dict)



#print(txtfiles)    
    



#print(json_received)

#send_client(destination_port=1501, input_dict=dict_list)