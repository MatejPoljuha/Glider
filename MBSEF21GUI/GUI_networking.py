import json
import base64
from PIL import Image
import socket

import random
from time import sleep
import queue


############### IMG helper function from and to json image

def img_to_json(filename):
    data = {}
    with open(filename, mode='rb') as file:
        img = file.read()
        data['img'] = base64.encodebytes(img).decode('utf-8')
    
    return json.dumps(data)
    
    
def json_to_image(data,filename):
    #data['img'] = base64.encodebytes(img).decode('utf-8')   
    dat = json.loads(data)['img'] 
    
    image = base64.b64decode(dat)
    with open(filename, mode='wb') as file:
        file.write(image) 
        
        
#########################Helpers end



################### THIS PART WILLprocess_image_and_extract_line_parameters BE USEFULL FOR MATEJ (my part has queue implemented, so take a look )

def SERVER_json_for_DPS_side():
    sock = socket.socket()
    print ("Socket created ...")
    
    port = 1500
    sock.bind(('127.0.0.1', port))
    sock.listen(5)
    
    print ('socket is listening')
    while True:
        c, addr = sock.accept()
        print ('got connection from ', addr)
    
        jsonReceived = c.recv(1024)
        jsonReceived = json.loads(jsonReceived)
        print ("DPS received -->", jsonReceived)
    
        c.close()
        
        
        
def CLIENT_json_send_dict_DPS_side(input_dict):
    
    jsonResult = input_dict
    jsonResult = json.dumps(jsonResult)
    
    try:
        sock = socket.socket()
    except socket.error as err:
        print ('Socket error because of %s' %(err))
    
    port = 1501
    address = "127.0.0.1"
    
    try:
        sock.connect((address, port))
        sock.send(jsonResult.encode('utf-8'))
    except socket.gaierror:
    
        print ('There an error resolving the host')
    
        #sys.exit() 
            
    print( jsonResult, 'DPS sent!')
    sock.close()


def My_simulator_of_DPS_messages_with():
    while True:
        dict_temp = {}
        dict_temp['aircraft_position'] = [random.randint(0, 400),random.randint(0, 400)]
        CLIENT_json_send_dict_DPS_side(dict_temp)
        sleep(3.0)

################### END -----THIS PART WILL BE USEFULL FOR MATEJ






################# MY GUI SIDE FUNCTIONS 
def SERVER_json_for_GUI_side(comm_queue):
    sock = socket.socket()
    print ("Socket created ...")
    
    port = 1501
    sock.bind(('127.0.0.1', port))
    sock.listen(5)
    
    print ('socket is listening')
    while True:
        c, addr = sock.accept()
        print ('got connection from ', addr)
    
        jsonReceived = c.recv(1024)
        jsonReceived = json.loads(jsonReceived)
        print ("Json received -->", jsonReceived)
        comm_queue.put(jsonReceived)
        c.close()


        
def CLIENT_json_send_dict_GUI_side(input_dict):
    
    jsonResult = input_dict
    jsonResult = json.dumps(jsonResult)
    
    try:
        sock = socket.socket()
    except socket.error as err:
        print ('Socket error because of %s' %(err))
    
    port = 1500
    address = "127.0.0.1"
    
    try:
        sock.connect((address, port))
        sock.send(jsonResult.encode('utf-8'))
    except socket.gaierror:
    
        print ('There an error resolving the host')
    
        #sys.exit() 
            
    print( jsonResult, 'was sent!')
    sock.close()
    
    
#################END MY GUI SIDE FUNCTIONS     