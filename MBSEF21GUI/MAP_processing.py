from svg.path import parse_path
from svg.path.path import Line
from xml.dom import minidom
from svgwrite.data.pattern import coordinate
import numpy as np
import math
from math import sqrt, sin, cos
from numpy import angle
import json
import os




def process_image_and_extract_line_segments(map_file):
    # read the SVG file
    doc = minidom.parse(map_file)
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    doc.unlink()
    
    
    coordinates_for_plot=[]
   
    # print the line draw commands
    for path_string in path_strings:
        path = parse_path(path_string)
        for e in path:
            if isinstance(e, Line):
                x0 = e.start.real
                y0 = e.start.imag
                x1 = e.end.real
                y1 = e.end.imag
                coordinates_for_plot.append((x0, y0, x1, y1))
                #print("(%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))
    return coordinates_for_plot      



def process_image_and_extract_line_parameters(map_file):
    # read the SVG file
    doc = minidom.parse(map_file)
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    doc.unlink()
 
 
    coefficients_list = []
    derived_line_angle_list = []
    middle_point_list = []
    node_list = []
    # print the line draw commands
    for path_string in path_strings:
        path = parse_path(path_string)
        for e in path:
            if isinstance(e, Line):
                x0 = e.start.real
                y0 = e.start.imag
                x1 = e.end.real
                y1 = e.end.imag
                
                x=[round(x0), round(x1)]
                y=[round(y0), round(y1)]

                if(x[0]==x[1]):
                    coefficients=[0,0]    
                    derived_line_angle = 90;
                elif(y[0]==y[1]):
                    coefficients=[0,0]    
                    derived_line_angle = 0;
                else:
                    coefficients = np.polyfit(x, y, 1)
                    derived_line_angle = -math.atan(coefficients[0])*(360/6.28)
                    
                middle_point = [(x0+x1)/2,(y0+y1)/2]
                node = [x,y]
                coefficients_list.append(coefficients)
                derived_line_angle_list.append(derived_line_angle)
                middle_point_list.append(middle_point)
                node_list.append(node)
                
                #print(derived_line_angle,coefficients,middle_point)
    return (coefficients_list,derived_line_angle_list,middle_point_list,node_list)     


def generate_test_vector_field_origin():
    
    block_size = 30 #10 by 10 pixel vector field block
    image_size = 512
    central_points_of_boxes= np.round(np.arange(0.5*(block_size),image_size-0.5*block_size,block_size)).astype(int) # same for x and y
    left_edge_points_of_boxes = np.round(central_points_of_boxes- block_size/2).astype(int)
    
    #central_points_of_boxes= np.round(np.arange(0.5*(image_size/block_size),image_size-0.5*(image_size/block_size),block_size)).astype(int) # same for x and y
    vect_field=np.zeros((len(central_points_of_boxes),len(central_points_of_boxes))).tolist()
    coordinates_for_plot=np.zeros((len(central_points_of_boxes),len(central_points_of_boxes))).tolist()

    
    # here we would fill it with real data of wind but its a mockup
    
    default_same_windspeed_and_angle = [45,100] # angle in degrees , speed
    
    for row in vect_field:
        for j, val in enumerate(row):
            row[j] = default_same_windspeed_and_angle
            
            
            
    for r, row in enumerate(coordinates_for_plot):
        for c, val in enumerate(row):
            
            wind_angle = vect_field[r][c][0]
            wind_speed = vect_field[r][c][1]
            
            
            x0 = central_points_of_boxes[r]
            y0 = central_points_of_boxes[c]
            
            line_len = block_size*(sqrt(2)/2)
            x1 = int(x0+line_len*math.cos(wind_angle*6.28/360))
            y1 = int(y0+line_len*math.sin(wind_angle*6.28/360))
            row[c] = ((x0, y0, x1, y1))
            
            
    return (vect_field, coordinates_for_plot,central_points_of_boxes,left_edge_points_of_boxes)  

def generate_test_vector_field(weather_data):
    fil_dir = os.path.dirname(os.path.abspath(__file__))
    #print(fil_dir)
    filename = fil_dir+'/dictionary.json'

    #while not data_queue.empty():
    #    rec = data_queue.get()
    #    weather_data = rec
    # with open(filename) as f:
    #     weather_data = json.load(f)
    wind_x = []
    wind_y = []
    wind_deg = []
    wind_speed = []

    block_size = 45
    image_size = 512
    central_points_of_boxes = np.round(np.arange(0.5 * block_size, image_size - 0.5 * block_size, block_size))
    left_edge_points_of_boxes = np.round(central_points_of_boxes - block_size / 2).astype(int)

    vect_field = np.zeros((len(central_points_of_boxes), len(central_points_of_boxes))).tolist()  # 11*11
    coordinates_for_plot = np.zeros((len(central_points_of_boxes), len(central_points_of_boxes))).tolist()
    n = 0

    # vector field
    for row in vect_field:
        for j, val in enumerate(row):
            deg = weather_data[n]['data']['deg']
            speed = weather_data[n]['data']['speed']
            angle_and_speed = [deg, speed]
            row[j] = angle_and_speed
            n = n+1
    # print(vect_field)

    # coordinates for plot
    n = 0
    for r, row in enumerate(coordinates_for_plot):
        for c, val in enumerate(row):
            wind_angle = vect_field[r][c][0]
            wind_speed = vect_field[r][c][1]
            if 0 < wind_angle <= 90:
                wind_angle = wind_angle
            elif 90 < wind_angle <= 180:
                wind_angle = -(180 - wind_angle)
            elif 180 < wind_angle <= 270:
                wind_angle = wind_angle-180
            elif 270< wind_angle <= 360:
                wind_angle = -(360-wind_angle)
            wind_angle = -wind_angle  # take inverse for plotting
            x0 = central_points_of_boxes[r]
            y0 = central_points_of_boxes[c]

            line_len = block_size * (sqrt(2) / 2)
            x1 = int(x0 + line_len * cos(wind_angle * 3.14 / 180))
            y1 = int(y0 + line_len * sin(wind_angle * 3.14 / 180))
            row[c] = (x0, y0, x1, y1)

    return vect_field, coordinates_for_plot, central_points_of_boxes, left_edge_points_of_boxes



def interraction_field_to_obstacle(vec_field_data):
    (vect_field, coordinates_for_plot,central_points_of_boxes,left_edge_points_of_boxes)     = vec_field_data
    
    fil_dir = os.path.dirname(os.path.abspath(__file__))
    
    (coefficients_list,derived_line_angle_list,middle_point_list,node_list) = process_image_and_extract_line_parameters(fil_dir+"/imag.svg")
    
    result_list=[]
    
    
    # print(left_edge_points_of_boxes)
    for n,segment_angle in enumerate(derived_line_angle_list):
        
        value_of_point = middle_point_list[n]
        x_found_index=0
        y_found_index=0
        
        for index,val in enumerate(left_edge_points_of_boxes):
            if value_of_point[0] < val:
                break
            else:
                x_found_index = index
        for index,val in enumerate(left_edge_points_of_boxes):
            if value_of_point[1] < val:
                break
            else:
                y_found_index = index
        '''
        wind=vect_field[x_found_index][y_found_index]
        wind_angle = wind[0]
        wind_strenght = wind[1]
        
        segment_relation = abs(cos((segment_angle-wind_angle)*6.28))
        #segment_relation = cos((90-abs(segment_angle-wind_angle))*3.14/180)
        '''

        wind = vect_field[x_found_index][y_found_index]
        wind_angle = wind[0]
        wind_strength = wind[1]
        if 0 < wind_angle <= 90:
            wind_angle = wind_angle
        elif 90 < wind_angle <= 180:
            wind_angle = -(180 - wind_angle)
        elif 180 < wind_angle <= 270:
            wind_angle = wind_angle - 180
        elif 270 < wind_angle <= 360:
            wind_angle = -(360 - wind_angle)

        if (wind_angle * segment_angle) >= 0:
            angle_dif = abs(wind_angle - segment_angle)
        if wind_angle > 0 and segment_angle < 0:
            angle_dif = wind_angle - segment_angle
            if angle_dif > 90:
                angle_dif = 180 - angle_dif
        if segment_angle > 0 and wind_angle < 0:
            angle_dif = segment_angle - wind_angle
            if angle_dif > 90:
                angle_dif = 180 - angle_dif
        segment_relation = angle_dif / 90 * wind_strength

        if segment_relation > 0.5:
            output_dict= {'x_pos': int(value_of_point[0]),'y_pos':int(value_of_point[1]),'rel_strength': segment_relation}  # wind speed are real numbers

        # x_pos and y_pos need to be real gps coordinates
        # rel_strength needs to be how many meters the glider rises (altitude) in this node

        # send the node data to Bartek and to Matej separately
        # for the GUI to display proper colours for uplift strength in nodes, rel_strength should be scaled down from 0 to 1
        
            result_list.append(output_dict)
    strengthlist = []
    for a in result_list:
        strength = a['rel_strength']
        strengthlist.append(strength)

    return  result_list  
        #print(x_found_index,y_found_index)
                
        #print(segment_angle,middle_point_list[n])
        
        
        
#interraction_field_to_obstacle()
#(default_same_windspeed_and_angle, coordinates_for_plot)   = generate_test_vector_field()
#print(coordinates_for_plot)
#process_image_and_extract_line_parameters('imag.svg')

  