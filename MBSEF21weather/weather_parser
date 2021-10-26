import requests
import os
from datetime import datetime

location = "Los Angeles"

complete_api_link = "http://api.openweathermap.org/data/2.5/weather?q=" + location + "&appid=ea4e59bc9fb5384aac71dbdef5416ac7"

api_link = requests.get(complete_api_link)
api_data = api_link.json()
# print (api_data)

if api_data['cod'] == '404':
    print("Invalid city: {}, please check your city name".format(location))
else:
    temp_city = ((api_data['main']['temp']) - 273.15)
    wind_spd = api_data['wind']['speed']
    wind_deg = api_data['wind']['deg']

    # print("Current temperature is: {:.2f} deg C".format(temp_city))
    # print("Current wind speed:",wind_spd,'kph',wind_deg,'deg')
