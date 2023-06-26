#This file will be the base file that calls all other functions. 
# from Hardware import Hardware as dev
import numpy as np
import pandas as pd
import cv2
import scipy.stats as stat
import time
import serial

import wallFollow_class as WF
import Hardware.RealSense as RS
import Hardware.Filter as Filter

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

#hardware
cam = RS.RSCam(Range= "Short")
cam.get_frames() #Reject first frame (it's really dark.)

#initialize a dataframe of 0s the size of the map
#6 rows, 9 plants, only 3 rows are relevant
map = pd.DataFrame(np.zeros((3,9)), 
                   index=[2,4,6], 
                   columns=['P1','P2','P3','P4','P5','P6','P7','P8','P9'])

ripe = 0
unripe = 1

#taken from mom_uart_commands
def send_command(command):
    pico.write(command.encode())
    print("Sent pico the command: ", command)
    sent = wait_for_start(5, command)
    error_count = 0
    if sent == "error":
        while error_count < 3:
            print("Small error in communication, retrying now!")
            error_count += 1
            sent = wait_for_start(5, command)
    elif sent == "bad send":
        return False
                        
    elif sent == "success":
        print("Pico Succesfully received and started my command!")
        completed = wait_for_completion(10, command) 
        if completed == "error":  
            print("Pico had a error. brians sad.")
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
    pass

def identify():
    #Colorsensing
    Lower_bulb= ripe
    Upper_bulb= ripe
    return [Lower_bulb, Upper_bulb]

def mapping(ripe, bulbCount):
    if rowCounter == 2:
        map.at[2,'P{}'.format(bulbCount)] = ripe[0] + ripe[1]
    elif rowCounter == 4:
        map.at[4,'P{}'.format(bulbCount)] = ripe[0] + ripe[1]
    elif rowCounter == 6:
        map.at[6,'P{}'.format(bulbCount)] = ripe[0] + ripe[1]

def harvest_cotton(ripeness):
    if ripeness[0] == ripe and ripeness[1] == ripe:
        send_command("harvest00") #Harvest Both
    elif ripeness[0] == unripe and ripeness[1] == ripe:
        send_command("harvest01") #Harvest Lower Bulb
    elif ripeness[0] == ripe and ripeness[1] == unripe:
        send_command("harvest10") #Harvest Upper Bulb
    elif ripeness[0] == unripe and ripeness[1] == unripe:
        send_command("harvest11") #Harvest Nothing
    
state = 'init'
bollCounter = 1
rowCounter = 1

while(1==1):
    match state:
        case 'init':
            #wait for button press
            state = 'get_to wall'

        case 'find_wall':
            send_command("get_to_wall")
            state ='harvest'

        case 'harvest':
            while bulbCounter < 9:
                adjust()
                ripeness = identify() #Colorsensing of each bulb
                mapping(ripeness, bulbCounter)  #map and store data
                harvest_cotton(ripeness)
                bulbCounter = bulbCounter + 1 

            rowCounter = rowCounter + 1
            if rowCounter == 1 or 3 or 5:
                state = 'outside_right'
            elif rowCounter == 2 or 4 :
                state = 'inside_left'
            elif rowCounter == 6:
                state = 'go_home'

        case 'outisde_right':
            send_command("outside_right")
            bulbCounter = 1
            state = 'harvest'

        case 'inside_left':
            send_command("inside_left")
            bulbCounter = 1
            state = 'harvest'

        case'go_home':
            send_command("go_home")
            # export CSV file in the prescribed format:
            #map.to_csv("/Users/carsontownsend/Desktop/FarmRoomba.csv", index_label="Row:", encoding="utf-8") #Path will need to be changed
