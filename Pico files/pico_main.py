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
mom = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=machine.Pin(12), rx=machine.Pin(1))
Arm = Armcontrol()
Drive = Driving_control()

# There is one harvest function, that will get input from the switch statement on what cotton bolls
# to harvest. This info is passed through and we can program 3 different harvest controls.
def harvest(high, low):
    if high == 1 and low == 1:
        print("Harvesting High and Low")
        Arm.harvest_time([0,0])
        
        time.sleep(5)
        print("done")
        
    elif high == 1:
        print("Harvesting High")
        Arm.harvest_time([1,0])

        time.sleep(5)
        print("done")
         
    elif low == 1:
        print("Harvesting Low")
        Arm.harvest_time([0,1])
        
        time.sleep(5)
        print("done")
        
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    # ^^^ Delete the waits in the individual if statements! ^^^
    return True

# Get to wall needs to have the roomba drive from starting position to the wall about 6-7 inches away so
# the wall follow code can kick in.
def get_to_wall():
    print("get to wall")
    Drive.Find_wall()
    
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    time.sleep(5)
    return True
# Go home needs to have the roomba dead reckon to a finishing corner
def go_home():
    print("I want to go home")
    Drive.Find_corner()
    
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    time.sleep(5)
    return True

# Outside Right is our function where the robot dead reckons to a new row of cotton on the opposite
# side of the wall it was just farming.
def outside_right():
    print("turn right")
    Drive.Right_corner()
    
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    time.sleep(5)
    return True
# Inside left is the 180 degree turn where the robot turns to face the wall it has yet to harvest 
# in the row it just drove down.
def inside_left():
    print("yes its a left turn, it may not look like it but it's left.")
    Drive.Left_corner()
    
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    time.sleep(5)
    return True
# Motors is the controls for the wall follow to use and send constant info. Another big thing for this
# function that needs to be done is that the function needs to constantly read readings from uart. After
# getting my code working for uart I believe theres a bit more of a action delay than I originally thought
# so I may setup a quicker second uart connection for the numbers to read from. But this should be unnecessary
# atm.
# The math of this function needs its variables double checked. atm I havent done this personally.
'''
# for use with realsence
def motors(velocity, direction):
    print("Driving motors!")
    v = velocity/1000
    d = direction/1000
    r = 3.5/2 # Done in inches atm
    w_r = (v*r) + d
    w_l = (v*r) - d
    
    ###############################################
    # Carsons code here
    # or whoever else may write this in the future
    # If carson chooses to update this. For the dead
    # reckoning functions he may choose to run those
    # off the pi and send variables, but I assume he
    # will run the motors from the pico itself if 
    # the command is given. But agency yk
    ###############################################
    
    # Temprarily to test my code. No need to keep once I confirm the code is complete.
    time.sleep(5)
    return True
  '''  
# Splices string simply for the motors command to get three variables. The command drive,
# the velocity, and direction.

# This is also outdated and not used, but I kept it here for posterity reasons? idk
def splice_string(string):
    if len(string) != 18:
        return None

    part1 = string[:6]
    part2 = string[6:12]
    part3 = string[12:]

    return part1, part2, part3
# Turn functions for the roomba to receive basic movement commands for the Adjust()
# function
def left(steps):
    Drive.turn(steps, dir = 'l')
    drive_commands.Stop()
    
    return True

def right(steps):
    Drive.turn(steps)
    drive_commands.Stop()
    
    return True

def forward(steps):
    Drive.DriveStraight(steps)
    drive_commands.Stop()
    
    return True
    
def back(steps)
    Drive.DriveStraight(steps, dir = 'b')
    drive_commands.Stop()
    
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
            if not data or data == b'\n':
                break
            message += data
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
  
        
        # This motors command is the toughest because it needs to splice the command from integers sent. Me and carter
        # decided 6 ints were more than necessary for motors velocity and direction, so we splice it into three sets of
        # 6 integers here.
        if completed == False:
            result = splice_string(message_str)
            if result is not None:
                drive, velocity, direction = result
                if drive == "motors":
                    completed = motors(int(velocity), int(direction))
            else:
                print("The string length is not 18 characters.")
                
            
        
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
    time.sleep(0.1)
    # Reloops looking for a new command.
