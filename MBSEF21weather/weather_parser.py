import requests
import time
import json
import socket
from datetime import datetime

# location = "Los Angeles"

# def send_client(destination_port: int, input_dict: dict, logging=True, host_ip='127.0.0.1'):
    # """
    # Converts input dictionary into json, creates a socket, sends the data to a destination port on a destination address.
    # :param destination_port: port to which the data is sent
    # :param input_dict: data to be sent
    # :param logging: if True, the prints happen, if False they don't
    # :param host_ip: host device address to which the data is sent
    # """
    # # converts input dictionary into json
    # json_to_send = json.dumps(input_dict)
    #
    # # creates socket object and allows it to be reused if program is relaunched (needed for Linux/Mac)
    # with socket.socket() as sock:
        # # try to connect to the server socket and send the dictionary(json) to it
        # try:
            # sock.connect((host_ip, destination_port))
            # sock.send(json_to_send.encode('utf-8'))
        # except ConnectionRefusedError:
            # # this is not subject to the logging parameter
            # print('Connection refused on port: ', destination_port)
            #
        # if logging:
            # print(json_to_send, 'was sent to server on port: ', destination_port)
            #
        # # close socket after sending the data
        # sock.close()

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
        #time.sleep(0.1)

        now = datetime.now()
        current_time = now.strftime("%y/%m/%d %H:%M:%S")

        # print (api_data)

        if api_data['cod'] == '404':
            pass
            #print("Invalid city: {}, please check your city name".format(location))
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


with open("weather.json", "w") as write_file:
    json.dump(dict_list, write_file)

#send_client(destination_port=1501, input_dict=dict_list)

# end
