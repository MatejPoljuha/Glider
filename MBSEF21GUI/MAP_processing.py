from svg.path import parse_path
from svg.path.path import Line
from xml.dom import minidom
from svgwrite.data.pattern import coordinate
import numpy as np
import math
from math import sqrt, sin, cos
from numpy import angle






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
                
                x=[x0, x1]
                y=[y0, y1]

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


def generate_test_vector_field():
    
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


def interraction_field_to_obstacle():
    (vect_field, coordinates_for_plot,central_points_of_boxes,left_edge_points_of_boxes)     = generate_test_vector_field()
    (coefficients_list,derived_line_angle_list,middle_point_list,node_list) = process_image_and_extract_line_parameters("imag.svg")
    
    result_list=[]
    
    
    print(left_edge_points_of_boxes)
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
        
        wind=vect_field[x_found_index][y_found_index]
        wind_angle = wind[0]
        wind_strenght = wind[1]
        
        segment_relation = abs(cos((segment_angle-wind_angle)*6.28))
        
        output_dict= {'x_pos': int(value_of_point[0]),'y_pos':int(value_of_point[1]),'rel_strength':segment_relation}

        
        result_list.append(output_dict)
        
    return  result_list  
        #print(x_found_index,y_found_index)
                
        #print(segment_angle,middle_point_list[n])
        
        
        
interraction_field_to_obstacle()
#(default_same_windspeed_and_angle, coordinates_for_plot)   = generate_test_vector_field()
#print(coordinates_for_plot)
#process_image_and_extract_line_parameters('imag.svg')

  