import tkinter as tk
from tkinter import ttk
from tkinter import * 
import logging
from PIL import Image, ImageTk
import threading
import sys
import time
from MBSEF21GUI.IMG_rendering import *
from MBSEF21GUI.GUI_networking import *
import queue
from communication import *



flight_mode = "Longest Flight"
app_closed=False

# this is the function called when the button is clicked
def ModeOne():
    global flight_mode,my_label
    flight_mode = "Longest Flight"
    my_label['text']=flight_mode

# this is the function called when the button is clicked
def ModeTwo():
    global flight_mode,my_label
    flight_mode = "Fastest Flight"
    my_label['text']=flight_mode


# this is the function called when the button is clicked
'''
def SetDestination():
    global destinationSET
    destinationSET  = False
    print('SetDestination')
'''

# this is a function to get the user input from the text input box
def getInputBoxValue():
    userInput = tInput.get()
    return userInput

def RunNavigation():
    
    message = {}
    message['flight_mode'] = flight_mode
    message['destination'] = destination_position

    send_client(1500, message)
    #print('Run navigation')
    
    
root = Tk()

# This is the section of code which creates the main window
root.geometry('1000x600')
root.configure(background='#F0F8FF')
root.title('Glider Navigation System')
root.resizable(width=False, height=False)

# First, we create a canvas to put the picture on
MapCanvas= Canvas(root, height=512, width=512)
# Then, we actually create the image file to use (it has to be a *.gif)
picture_file = PhotoImage(file = 'map.PNG')  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
# Finally, we create the image on the canvas and then place it onto the main window
image_on_canvas = MapCanvas.create_image(512, 0, anchor=NE, image=picture_file)
MapCanvas.place(x=10, y=10)
Label(root, text="click on map to set destination", bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=100, y=530)


# This is the section of code which creates a button
Button(root, text='Longest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeOne).place(x=850, y=100)


# This is the section of code which creates a button
Button(root, text='Fastest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeTwo).place(x=850, y=150)


# This is the section of code which creates the a label
my_label  = Label(root, text=flight_mode, bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=850, y=200)

# This is the section of code which creates a text input box
tInput=Entry(root)
tInput.place(x=850, y=250)

#Button(root, text='Set Destination', bg='#F0F8FF', font=('arial', 12, 'normal'), command=SetDestination).place(x=850, y=350)
Button(root, text='Run Navigation', bg='#F0F8FF', font=('arial', 12, 'normal'), command=RunNavigation).place(x=850, y=400)






destination_position=[0,0]



aircraft_position = [0,0]



def callback(event):
    global destination_position, aircraft_position,destinationSET
    print ("clicked at", event.x, event.y)
    destination_position = [event.x,event.y]

    
    


MapCanvas.bind("<Button-1>", callback)




def refreshCanvas():
    global number
    global MapCanvas
    global image_on_canvas
    global picture_file
    global data_queue
  
    global destination_position, aircraft_position,destinationSET
  
    #aircraft_position = [300 ,100]
    
    rec=None
    while not data_queue.empty():
        rec = data_queue.get()
        aircraft_position = rec['aircraft_position']
   
    imgA = make_overlay(destination_position, aircraft_position)
    
    picture_file = ImageTk.PhotoImage(imgA)

    
    MapCanvas.itemconfig(image_on_canvas, image = picture_file)
    
    root.after(50, refreshCanvas)
    
    
'''    
def thread_function(name):
    global app_closed
    
    for i in range(1,10):
        print("runner {}".format(i))
        time.sleep(2)
        if app_closed:
            break
    


x = threading.Thread(target=thread_function, args=(1,))
x.start()
'''

data_queue = queue.Queue()

y = threading.Thread(target=receive_server, args=(1501, data_queue, True))
y.daemon = True
y.start()




### SIMULATED DPS (CENTRAL COMPUTER)
y = threading.Thread(target=receive_server, args=(1500, True))
y.daemon = True
y.start()

# sleep(3)
y = threading.Thread(target=simulate_dps_messages, args=())
y.daemon = True
y.start()

########
         
         
         
         
refreshCanvas()
root.mainloop()

app_closed=True

#x.join()
#sys.exit()