import subprocess

#from MBSEF21weather.weather_streamer import *
#from MBSEF21DPS.data_processing_system import *
#from MBSEF21GUI.GUI import *
import os
#os.system("start python MBSEF21GUI/GUI.py ") 
subprocess.Popen(["python", "MBSEF21DPS/data_processing_system.py"] )
subprocess.Popen(["python", "MBSEF21weather/weather_streamer.py"] )
subprocess.Popen(["python", "MBSEF21GUI/GUI.py"] )
#subprocess.Popen(["python", "MBSEF21GUI/GUI.py"])
#print("der")
#subprocess.call("data_processing_system.py")
#subprocess.call("weather_streamer.py")




#subprocess.call("GUI.py")