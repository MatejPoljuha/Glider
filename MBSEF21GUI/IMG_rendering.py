from PIL import Image,ImageDraw

from MBSEF21GUI.MAP_processing import *


def make_overlay(destination_position, aircraft_position, uplift, navigation_line, vec_field_data, experiment_flag):
    fil_dir = os.path.dirname(os.path.abspath(__file__))

    background = Image.open(fil_dir+"/map.png").convert('RGB')

    draw = ImageDraw.Draw(background) 

    if experiment_flag == '2':
        line_segments = process_image_and_extract_line_segments(fil_dir+'/imagFORGED.svg')
    else:
        line_segments = process_image_and_extract_line_segments(fil_dir+'/imag.svg')

    for element in line_segments:    
        draw.line(element, fill=(0, 255, 0), width=5)

    for element in navigation_line:
        draw.line(element, fill=(255, 204, 0), width=2)

    rel_strenght_list = []
    for a in uplift:
        rel_strenght_list.append(a['rel_strength'])
        
        
    
    for a in uplift:
        strength = a['rel_strength']
        x=a['x_pos']
        y=a['y_pos']
        r=3#a['rel_strength']*3 + 3
        if(max(rel_strenght_list) != min(rel_strenght_list)):
            color = (strength-min(rel_strenght_list))*255 /(max(rel_strenght_list) - min(rel_strenght_list))
        else:
            color = 255
        
        # print(color)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(int(color),0,0,0), outline=(0, 0, 255, 255))



   
    # (vect_field, coordinates_for_plot,central_points_of_boxes,left_edge_points_of_boxes)=vec_field_data#   = generate_test_vector_field()
        
    for row in vec_field_data:
        for j, val in enumerate(row):
            draw.line(val, fill=(0, 0, 255), width=2)
    #for row in coordinates_for_plot:
    #    draw.line(row[0], fill=(0, 0, 255), width=5) 
    
    if destination_position[0]>background.size[0]:
        destination_position[0] = background.size[0]-1
    elif destination_position[1]>background.size[1]:
        destination_position[1] = background.size[1]-1
    
    foreground = Image.open(fil_dir+"/placeholder.png")
    foreground = foreground.resize((30,30), Image.ANTIALIAS)
    destination_position_internal = [destination_position[0]-15,destination_position[1]-30]
    background.paste(foreground, tuple(destination_position_internal), foreground)





    if aircraft_position[0]>background.size[0]:
        aircraft_position[0] = background.size[0]-1
    elif aircraft_position[1]>background.size[1]:
        aircraft_position[1] = background.size[1]-1
        
    #print("DP",destination_position , "AP",aircraft_position)   
    foreground = Image.open(fil_dir+"/aeroplane.png")
    foreground = foreground.resize((30,30), Image.ANTIALIAS)
    aircraft_position_internal = [aircraft_position[0],aircraft_position[1]-15]
    background.paste(foreground, tuple(aircraft_position_internal), foreground)




    return background