# Pico Main, or Mom's Command
# * Calling it a master slave is weird, so now pico has a mom, yay
# Brian Jones - Created 6/6/2023 - Edited on 6/6/2023
# Goal is to have an easy way to add new commands to the pico that
# pico can look for and then respond that it is acting, and then
# that the command has been completed.
# 

import machine
import time
from Driving import Driving_control
from Arm_control import Armcontrol

# Creates a uart connection with Mom, that it will save to, and then respond back that it has been received
mom = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=machine.Pin(0), rx=machine.Pin(1))
Arm = Armcontrol()
Drive = Driving_control()

# There is one harvest function, that will get input from the switch statement on what cotton bolls
# to harvest. This info is passed through and we can program 3 different harvest controls.
def harvest(high, low):
    if high == 1 and low == 1:
        print("Harvesting High and Low")
        Arm.harvest_time([0,0])
        
        #time.sleep(5)
        print("done")
        
    elif high == 1:
        print("Harvesting High")
        Arm.harvest_time([1,0])

        #time.sleep(5)
        print("done")
         
    elif low == 1:
        print("Harvesting Low")
        Arm.harvest_time([0,1])
        
        #time.sleep(5)
        print("done")
        
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    # ^^^ Delete the waits in the individual if statements! ^^^
    return True

# Get to wall needs to have the roomba drive from starting position to the wall about 6-7 inches away so
# the wall follow code can kick in.
def get_to_wall():
    print("get to wall")
    Drive.Find_wall()
    #time.sleep(5)
    return True
    
# Go home needs to have the roomba dead reckon to a finishing corner
def go_home():
    print("I want to go home")
    Drive.Find_corner()
    #time.sleep(5)
    return True

def outside_right():
    print("turn right")
    Drive.Right_corner()
    return True

def inside_left():
    print("yes its a left turn, it may not look like it but it's left.")
    Drive.Left_corner()
    return True

def left(steps):
    Drive.turn(steps, dir = 'l')
    Drive.Stop()
    return True

def right(steps):
    Drive.turn(steps)
    Drive.Stop()
    return True

def forward(steps):
    Drive.DriveStraight(steps)
    Drive.Stop()
    return True
    
def back(steps):
    Drive.DriveStraight(steps, dir = 'b')
    Drive.Stop()
    return True

# Main function here. This always runs and is looking for a new command from the pi which will be pretty
# constant. Every time it receives a command it reports the valid command back and then ignores it's 
# transmitter and completes it's task. It then reports the task is complete and looks for a new command.
# There will need to be seperate uart code in motors function looking for updates to the variables it recieves.
print("Started")
while True:             # Keeps it always running
    completed = False   # Resets to false for every new command
    if mom.any():       # Looks for any coms
        # Confusing but 100% accurately saves all strings sent to it from mom.
        message = b""
        while True:
            data = mom.read(1)
            if data:
                message += data
            else: 
                break
            if data == b'\n':
                break
            time.sleep(0.001)
        message_str = message.decode('utf-8').strip()   # message_str stays unaltered to reuse in coms back to mom.
        
        # Small delay is to ensure mom has time to listen after sending. However this may be obsolete, I will check tomorrow.
        print("Received message:", message_str, " from mom.")
        time.sleep(0.2)
        response = "starting " + message_str
        print(response)
        mom.write(response.encode())
        
        # Switch table of commands. It's messy but python has no clean switch table thats any better implementation than this.
        # C++ Superior. Once it goes through all of the basic commands it goes to out complicated one for the motors which has
        # a one check, and after it is supposed to report back bad send if the command does not exist. The code here looks like
        # It does it but my code for Mom seems to net recognize it atm, but it loops through its 3 time failsafe anyways so it's
        # not a hige concern. Also I will redice the wait timings at a future date to try to speed up operations after they are
        # working.
        if   message_str == "harvest01":		# Harvest Low
            completed = harvest(0, 1)
        elif message_str == "harvest10":		# Harvest High
            completed = harvest(1, 0)
        elif message_str == "harvest00":		# Harvest Both High and Low
            completed = harvest(0, 0)
        elif  message_str == "harvest11":		# Harvest Nothing
            completed = harvest(1, 1)
            
        # direction commands for the brand new Adjust() function
        elif message_str[:4] == "left":
            completed = left(int(message_str[4:]))
        elif message_str[:5] == "right":
            completed = right(int(message_str[5:]))
        elif message_str[:7] == "forward":
            completed = forward(int(message_str[7:]))
        elif message_Str[:4] == "back":
            completed = back(int(message_str[4:]))
            
        elif message_str == "get_to_wall":		# Starts from corner and needs to get within real sense range of the first wall
            completed = get_to_wall()
        elif message_str == "outside_right":	# Is supposed to turn 180 degrees to the new row
            completed = outside_right()
        elif message_str == "inside_left":		# Is supposed to turn 180 degrees to opposite wall
            completed = inside_left()
        elif message_str == "go_home":			# Is supposed to bring the robot to the final corner
            completed = go_home()
            # elif message_str == "go_forward":		# Will move robot to next possible boll location
            
        
        # If no commands are recognized... bad send
        if completed == True:
            response = "completed " + message_str
            mom.write(response.encode())
            print("I have completed my task and am ready for a new one!\n")
        else:
            print("badsend")
            mom.write("bad send".encode())
        # send complete
    # Another delay, not sure it's necessary.

    # time.sleep is commented out, it will make print statements glitch but uart
    # will run faster!
    # time.sleep(0.1)
    # Reloops looking for a new command.
