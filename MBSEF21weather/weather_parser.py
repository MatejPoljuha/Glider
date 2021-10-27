import requests
import os
from datetime import datetime

location = "Los Angeles"

# hardcode lat and long of the map of los angeles. Make several hundred calls over a few minutes and save it so we dont have to wait for it to update.
# 20 x 20 grid. to save weather data, make a message containing longditude(box_y), latitude(box_x), speed, angle, timestamp. Also you can
# store json files.

# complete_api_link = "http://api.openweathermap.org/data/2.5/weather?q=" + location + "&appid=ea4e59bc9fb5384aac71dbdef5416ac7"
complete_api_link = "http://api.openweathermap.org/data/2.5/weather?lat=55.78145136189998&lon=12.505930224090992&appid=ea4e59bc9fb5384aac71dbdef5416ac7"
# 55.77145136189998, 12.505930224090992
# 55.78663678274084, 12.647751961063
api_link = requests.get(complete_api_link)
api_data = api_link.json()
# print (api_data)

if api_data['cod'] == '404':
    print("Invalid city: {}, please check your city name".format(location))
else:
    temp_city = ((api_data['main']['temp']) - 273.15)
    wind_spd = api_data['wind']['speed']
    wind_deg = api_data['wind']['deg']

    print("Current temperature is: {:.2f} deg C".format(temp_city))
    print("Current wind speed:",wind_spd,'m/s',wind_deg,'deg')

# message={}
# message['']

