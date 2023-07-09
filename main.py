#This file will be the base file that calls all other functions. 
# from Hardware import Hardware as dev
import numpy as np
import pandas as pd
import cv2
import scipy.stats as stat
import time
import serial

import RealSense as RS
import Filter
import measurements

# Initializes pins for uart coms to be used, 9600 baud rate
pico = serial.Serial('/dev/serial0', 9600, timeout = 1)

#States
class states:
    init = 0            #wait for start button
    get_to_wall = 1       #Move to the wall and the first bulb
    harvest = 2         #Move along and harvest each bulb
    outside_right = 3      #Turn right and move to the next row
    inside_left = 4       #Move out of the run and do a 180 degree turn and move back in
    go_home = 5          #Move from the end of the last row to the final location. Store the map to a file

#initialize a dataframe of 0s the size of the map
#6 rows, 9 plants, only 3 rows are relevant
map = pd.DataFrame(np.zeros((3,10)), 
                   index=[2,4,6], 
                   columns=['Row:','P1','P2','P3','P4','P5','P6','P7','P8','P9'])

ripe = 0
unripe = 1
empty = 2

# Tuning: number of steps per unit
INCH = 145 # steps per inch
DEGREE = 14.4 # steps per degree

#taken from mom_uart_commands
def send_command(command):
    # Values to chage how long the pi waits for each type of pico message, a start and finish
    start_timeout = 0.5
    complete_timeout = 20

    # Starts writing command to pico
    pico.write(command.encode())
    print("Sent pico the command: ", command)
    '''
    sent = wait_for_start(start_timeout, command)
    error_count = 0

    # This is an error to try to see if the pico will return the correct response after 3 attempts
    if sent == "error":
        while error_count < 3:
            print("Small error in communication, retrying now!")
            error_count += 1
            sent = wait_for_start(start_timeout, command)
    elif sent == "bad send":
        return False
                        
    elif sent == "success":
        print("Pico Succesfully received and started my command!")
        completed = wait_for_completion(complete_timeout, command) 
        if completed == "error":  
            print("Pico had an error. brian is sad.")
            return False
        elif completed == "success":
            print("Success! Mom had 100% faith.")
            return True
    '''
    completed = wait_for_completion(complete_timeout, command) 
    if completed == "error":  
        print("Pico had an error. brian is sad.")
        return False
    elif completed == "success":
        print("Success! Mom had 100% faith.")
        return True

def wait_for_start(timeout_duration, command):
    print("\nNow looking for the start signal...")

    start_time = time.time()
    while (time.time() - start_time) < timeout_duration:
        if pico.in_waiting > 0:
            message = pico.readline().decode().strip()
            print("recieved message: ", message)
            
            if message == "starting " + command:
                print("pico started correct command!")
                return "success"
            elif message == "bad send":
                print("unknown command was sent.")
                return "bad send"
            elif message != "starting " + command:
                print("pico messaged the wrong message!", message)
                return "error"
                    
    if (time.time() - start_time) >= timeout_duration:
        print("Error: timeout of message.")
        return "error"
    
def wait_for_completion(timeout_duration, command):
    print("\nNow looking for completion signal...")
    start_time = time.time()
    while (time.time() - start_time) < timeout_duration:
        if pico.in_waiting > 0:
            message = pico.readline().decode().strip()
            print("recieved message: ", message)
            
            if message == "completed " + command:
                print("easy dub, task was completed succesfully.")
                return "success"
            elif message != "completed " + command:
                print("reached too close to the sun here, didn't work")
                return "error"
            
    if (time.time() - start_time) >= timeout_duration:
        print("Error: timeout of message.")
        return "error"
                
def adjust():
    #constants needs for the function
    theta_man = 30	# Roomba will always turn at a 30 degree angle for calculation purposes
    # X is measured distance of roomba to the wall.
    x_des = 7.375  # desired distance from the wall, in inches
    x_max = 0.25
    x_min = 0.25
    # Measured angle in parallel to the wall. positive leans left,
    # negative will lean right in parallel to the wall
    theta_max = 1
    theta_min = -1
    # Measured dist to the next boll if it be off.
    y_min = -0.25
    y_max = 0.25

    # Start by measuring position relative to wall
    x_meas, theta_meas = measurements.measure_x_theta()
    
    # If distance is greater than desired
    if x_meas > x_des + x_max:
        # calculate stuff
        delta_x = x_meas - x_des
        forward_dist = INCH * delta_x / np.tan(np.radians(theta_man))       
        back_dist = forward_dist / np.cos(np.radians(theta_man))
        theta_turn = DEGREE * (theta_man + theta_meas)
        theta_man_turn = DEGREE * theta_man 
        
        send_command("left" + str(theta_turn))
        send_command("back" + str(back_dist))
        send_command("right" + str(theta_man_turn))
        send_command("forward" + str(forward_dist))

    #If the distance is less than desired        
    elif x_meas < x_des - x_min:
        # calculate stuff
        delta_x = x_meas - x_des
        forward_dist = -INCH * delta_x / np.tan(np.radians(theta_man))
        back_dist = forward_dist / np.cos(np.radians(theta_man)) 
        theta_turn = DEGREE * (theta_man - theta_meas)
        theta_man_turn = DEGREE * theta_man
        
        send_command("right" + str(theta_turn))
        send_command("back" + str(back_dist))
        send_command("left" + str(theta_man_turn))
        send_command("forward" + str(forward_dist))
        
    # Will update the angle if roomba is more than a degree off either way.
    elif theta_meas > theta_max:
        send_command("left" + str(DEGREE*theta_meas))
    elif theta_meas < theta_min:
        send_command("right" + str(-DEGREE*theta_meas))

    y_meas = measurements.measure_y()
    #Updates Y distance after
    if y_meas > y_max:
        send_command("back" + str(INCH*y_meas))
    elif y_meas < y_min:
        send_command("forward" + str(-INCH*y_meas))

def identify():
    # Color Sensing
    ripe_bolls, unripe_bolls = measurements.measure_ripe()

    # Map Identification
    empty = 0 # for mapping, we only care about unripe bolls, so "empty" has the same value as "ripe"
    if ripe_bolls < 10:
        upper_boll = ripe
    elif unripe_bolls < 10:
        upper_boll = unripe
    else: 
        upper_boll = empty
    if ripe_bolls % 10 < 1:
        lower_boll = ripe
    elif unripe_bolls % 10 < 1:
        lower_boll = unripe
    else: 
        lower_boll = empty
    ripeness_map = [lower_boll, upper_boll]

    # Harvest Identification
    empty = 2 # for harvesting, ripe and empty are different
    if ripe_bolls < 10:
        upper_boll = ripe
    elif unripe_bolls < 10:
        upper_boll = unripe
    else: 
        upper_boll = empty
    if ripe_bolls % 10 < 1:
        lower_boll = ripe
    elif unripe_bolls % 10 < 1:
        lower_boll = unripe
    else: 
        lower_boll = empty
    ripeness_harvest = [lower_boll, upper_boll]

    print("Upper Boll: ", upper_boll)
    print("Lower Boll: ", lower_boll)
    return ripeness_map, ripeness_harvest

def mapping(ripeness, bollCount):
    if rowCounter == 2:
        map.at[2,'P{}'.format(bollCount)] = ripeness[0] + ripeness[1]
    elif rowCounter == 4:
        map.at[4,'P{}'.format(bollCount)] = ripeness[0] + ripeness[1]
    elif rowCounter == 6:
        map.at[6,'P{}'.format(bollCount)] = ripeness[0] + ripeness[1]

def harvest_cotton(ripeness):
    if ripeness[0] == ripe and ripeness[1] == ripe:
        send_command("harvest00") #Harvest Both
    elif ripeness[0] == unripe and ripeness[1] == ripe:
        send_command("harvest01") #Harvest Lower Bulb
    elif ripeness[0] == ripe and ripeness[1] == unripe:
        send_command("harvest10") #Harvest Upper Bulb
    elif ripeness[0] == unripe and ripeness[1] == unripe:
        send_command("harvest11") #Harvest Nothing
    
state = 'harvest'#'init'
bollCounter = 1
rowCounter = 2

while True:
    match state:
        case 'init':
            #wait for button press
            state = 'get_to wall'

        case 'get_to_wall':
            send_command("get_to_wall")
            state ='harvest'

        case 'harvest':
            while bollCounter < 10:
                if bollCounter in {2,3,4,5,6,7,8}:
                    adjust()
                    pass
            
                if rowCounter == 1:
                    send_command("forward" + str(INCH * 8.25))
                    harvest_cotton([1,0]) # just lower row, don't need to sense
                elif rowCounter == 3:
                    send_command("forward" + str(INCH * 8.25))
                    harvest_cotton([0,0]) # upper and lower rows, don't need to sense
                else: # other rows have unripe or missing, need to sense
                    ripeness_map, ripeness_harvest = identify() # Color Sensing of each bulb
                    #mapping(ripeness_map, bollCounter)  # Map and store data
                    send_command("forward" + str(INCH * 8.25))
                    harvest_cotton(ripeness_harvest)
                
                if bollCounter < 9:
                    send_command("back" + str(INCH * 3.25))
                    pass
                
                bollCounter = bollCounter + 1 

            if rowCounter in {1, 3, 5}:
                state = 'outside_right'
            elif rowCounter in {2, 4}:
                state = 'inside_left'
            elif rowCounter == 6:
                state = 'go_home'
            rowCounter = rowCounter + 1

        case 'outside_right':
            send_command("outside_right") 
            bollCounter = 1
            state = 'harvest'

        case 'inside_left':
            send_command("inside_left")
            bollCounter = 1
            state = 'harvest'

        case 'go_home':
            pass
            # send_command("go_home")
            # export CSV file in the prescribed format:
            #map.to_csv("/Users/carsontownsend/Desktop/FarmRoomba.csv", index_label="Row:", encoding="utf-8") #Path will need to be changed
