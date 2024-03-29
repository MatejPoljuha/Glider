from tkinter import *
import sys
import threading
from tkinter import *

from PIL import ImageTk

from MBSEF21DPS.data_processing_system import run_data_processing_system
from MBSEF21GUI.IMG_rendering import *
from MBSEF21pathplanning.path_planning import run_path_planning
from MBSEF21weather.weather_streamer import run_weather_streamer
from communication import *

# flight_mode = "Fastest Flight"
app_closed = False
navigation_line = []

global experiment_flag
experiment_flag = '0'
# launch parameter that determines the rate in seconds of weather situation(data) changing
weather_refresh_interval = int(sys.argv[1])
time_spent_at_node = int(sys.argv[2])
if len(sys.argv) >= 4:
    experiment_input_flag = sys.argv[3]
    if experiment_input_flag[-1] == "1":
        experiment_flag = '1'
    elif experiment_input_flag[-1] == "2":
        experiment_flag = '2'
    elif experiment_input_flag[-1] == "3":
        experiment_flag = '3'





# this is the function called when the button is clicked
"""def ModeOne():
    global flight_mode,my_label
    flight_mode = "Longest Flight"
    my_label['text']=flight_mode

# this is the function called when the button is clicked
def ModeTwo():
    global flight_mode,my_label
    flight_mode = "Fastest Flight"
    my_label['text']=flight_mode"""


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
    global tInput
    message = {'destination': destination_position,
               'dest_altitude': tInput1.get(),
               'start_altitude': tInput2.get(),
               'starting_position': starting_position}
    # message['flight_mode'] = flight_mode
    send_client(1500, message, logging=False)
    
    
root = Tk()

# This is the section of code which creates the main window
root.geometry('1100x600')
root.configure(background='#F0F8FF')
root.title('Glider Navigation System')
root.resizable(width=False, height=False)

# First, we create a canvas to put the picture on
MapCanvas = Canvas(root, height=512, width=512)

# Then, we actually create the image file to use (it has to be a *.gif)
fil_dir = os.path.dirname(os.path.abspath(__file__))
fil_dir = fil_dir + '/MBSEF21GUI'

picture_file = PhotoImage(file=fil_dir+'/map.png')
# Finally, we create the image on the canvas and then place it onto the main window
image_on_canvas = MapCanvas.create_image(512, 0, anchor=NE, image=picture_file)
MapCanvas.place(x=10, y=10)
Label(root, text="click on map to set destination", bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=100, y=530)


# This is the section of code which creates a button
# Button(root, text='Longest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeOne).place(x=800, y=100)


# This is the section of code which creates a button
# Button(root, text='Fastest Flight', bg='#F0F8FF', font=('arial', 12, 'normal'), command=ModeTwo).place(x=800, y=150)
my_label = Label(root, text="Starting position (1-511,1-511)", bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=800, y=200)

tInput0 = Entry(root, textvariable=StringVar(root, value='150,150'))
tInput0.place(x=800, y=250)

# This is the section of code which creates the a label
"""my_label  = Label(root, text=flight_mode, bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=800, y=200)"""

# This is the section of code which creates a text input box
my_label = Label(root, text="destination alt", bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=800, y=300)

tInput1 = Entry(root, textvariable=StringVar(root, value='20'))
tInput1.place(x=800, y=350)


my_label = Label(root, text="start alt", bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=800, y=400)

tInput2 = Entry(root, textvariable=StringVar(root, value='700'))
tInput2.place(x=800, y=450)

my_label = Label(root, text="Destination position (1-511,1-511)", bg='#F0F8FF', font=('arial', 12, 'normal'))
my_label.place(x=800, y=100)

tInput4 = Entry(root, textvariable=StringVar(root, value='50,50'))
tInput4.place(x=800, y=150)




#Button(root, text='Set Destination', bg='#F0F8FF', font=('arial', 12, 'normal'), command=SetDestination).place(x=850, y=350)
Button(root, text='Run Navigation', bg='#F0F8FF', font=('arial', 12, 'normal'), command=RunNavigation).place(x=800, y=500)






destination_position=[0,0]



aircraft_position = [50,50]
uplift_position=[]
navigation_line=[]
vec_field_data=([],[],[],[])
def callback(event):
    global destination_position, aircraft_position, destinationSET
    tInput4.delete(0, END)
    tInput4.insert(0, '{},{}'.format(event.x, event.y))


    
    


MapCanvas.bind("<Button-1>", callback)




def refreshCanvas():
    global number
    global MapCanvas
    global image_on_canvas
    global picture_file
    global data_queue_GUI
    global navigation_line
   
    global starting_position, destination_position, aircraft_position, destinationSET, uplift_position, navigation_line, vec_field_data
  
    #aircraft_position = [300 ,100]
    
    rec = None
    while not data_queue_GUI.empty():
        rec = data_queue_GUI.get()
        # aircraft_position = rec['aircraft_position']
        uplift_position = rec['uplift_position']
        vec_field_data = rec['vec_field_data']

    path_rec = None
    while not path_queue.empty():
        path_rec = path_queue.get()
        navigation_line = path_rec['shortest_path']
        path_display_form = []
        for index, element in enumerate(navigation_line[:-1]):
            path_display_form.append((element[0], element[1], navigation_line[index + 1][0], navigation_line[index + 1][1]))
        navigation_line = path_display_form

    # needs this try-except block if something other than a number is put into the input box
    try:
        starting_position = [min(int(tInput0.get().split(',')[0]), 511), min(int(tInput0.get().split(',')[1]), 511)]
        destination_position = [min(int(tInput4.get().split(',')[0]), 511), min(int(tInput4.get().split(',')[1]), 511)]
    except (ValueError, IndexError):
        starting_position = [1, 1]
        destination_position = [1, 1]

    imgA = make_overlay(destination_position, starting_position, uplift_position, navigation_line, vec_field_data,
                        experiment_flag)

    picture_file = ImageTk.PhotoImage(imgA)

    MapCanvas.itemconfig(image_on_canvas, image=picture_file)
    
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

data_queue_GUI = queue.Queue()
path_queue = queue.Queue()

y = threading.Thread(target=receive_server, args=(1501, data_queue_GUI, False))
y.daemon = True
y.start()

x = threading.Thread(target=receive_server, args=(1508, path_queue, False))
x.daemon = True
x.start()

# serve_sim_queue = queue.Queue()
### SIMULATED DPS (CENTRAL COMPUTER)
#y = threading.Thread(target=receive_server, args=(1500, serve_sim_queue, True))
#y.daemon = True
#y.start()

# sleep(3)
# y = threading.Thread(target=simulate_dps_messages, args=())
# y.daemon = True
# y.start()

########
         
# threads that start data processing, weather and path planning modules
dps_thread = threading.Thread(target=run_data_processing_system, args=(experiment_flag, ))
dps_thread.daemon = True
dps_thread.start()

weather_streamer_thread = threading.Thread(target=run_weather_streamer, args=(weather_refresh_interval, experiment_flag,))
weather_streamer_thread.daemon = True
weather_streamer_thread.start()

path_planning_thread = threading.Thread(target=run_path_planning, args=(weather_refresh_interval, time_spent_at_node))
path_planning_thread.daemon = True
path_planning_thread.start()

refreshCanvas()
root.mainloop()

app_closed=True

#x.join()
#sys.exit()