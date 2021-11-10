import requests
import time
import json
from datetime import datetime

# location = "Los Angeles"

# hardcode lat and long of the map of los angeles. Make several hundred calls over a few minutes and save it so we dont have to wait for it to update.
# 20 x 20 grid. to save weather data, make a message containing longditude(box_y), latitude(box_x), speed, angle, timestamp. Also you can
# store json files.

dict_list = []

for i in range(0, 11, 1):
    for j in range(0, 11, 1):
        lat = 34.031959 + 0.0569743 * i
        lat_str = str(lat)
        long = -118.664407 + 0.0699049 * j
        long_str = str(long)
        complete_api_link = "http://api.openweathermap.org/data/2.5/weather?lat=" + lat_str + "&lon=" + long_str + "&appid=ea4e59bc9fb5384aac71dbdef5416ac7"

        api_link = requests.get(complete_api_link)
        api_data = api_link.json()
        time.sleep(0.1)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # print (api_data)

        if api_data['cod'] == '404':
            print("Invalid city: {}, please check your city name".format(location))
        else:

            temp_city = ((api_data['main']['temp']) - 273.15)
            wind_spd = api_data['wind']['speed']
            wind_deg = api_data['wind']['deg']



            i_str = str(i)
            j_str = str(j)

            dict = {
                    "x": i,
                    "y": j,
                    "data": {
                            "speed": wind_spd,
                            "deg": wind_deg
                            }
                    }

            dict_list.append(dict)

            print(current_time,
                  "Lat:", lat_str,
                  "Long:", long_str,
                  " Current wind speed:", wind_spd, 'm/s',
                  wind_deg, 'deg')

with open("dictionary.json", "w") as write_file:
    json.dump(dict_list, write_file)
# end
