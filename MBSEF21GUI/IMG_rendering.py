from PIL import Image




def make_overlay(destination_position, aircraft_position):
    

    
    
    background = Image.open("map.png")
    
    
    
    
   
   
    
    if destination_position[0]>background.size[0]:
        destination_position[0] = background.size[0]-1
    elif destination_position[1]>background.size[1]:
        destination_position[1] = background.size[1]-1
    
    foreground = Image.open("placeholder.png")
    foreground = foreground.resize((30,30), Image.ANTIALIAS)
    destination_position_internal = [destination_position[0],destination_position[1]-30]
    background.paste(foreground, tuple(destination_position_internal), foreground)





    if aircraft_position[0]>background.size[0]:
        aircraft_position[0] = background.size[0]-1
    elif aircraft_position[1]>background.size[1]:
        aircraft_position[1] = background.size[1]-1
        
    #print("DP",destination_position , "AP",aircraft_position)   
    foreground = Image.open("aeroplane.png")
    foreground = foreground.resize((30,30), Image.ANTIALIAS)
    aircraft_position_internal = [aircraft_position[0],aircraft_position[1]-15]
    background.paste(foreground, tuple(aircraft_position_internal), foreground)


    return background