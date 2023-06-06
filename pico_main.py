# Pico Main, or Mom's Command
# * Calling it a master slave is weird, so now pico has a mom, yay
# Brian Jones - Created 6/6/2023 - Edited on 6/6/2023
# Goal is to have an easy way to add new commands to the pico that
# pico can look for and then respond that it is acting, and then
# that the command has been completed.
# 

import machine
import time

# Creates a uart connection with Mom, that it will save to, and then respond back that it has been received
mom = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=machine.Pin(12), rx=machine.Pin(1))

def harvest(high, low):
    if high == 1 and low == 1:
        print("Harvesting High and Low")
        time.sleep(5)
        print("done")
        
    elif high == 1:
        print("Harvesting High")
        time.sleep(5)
        print("done")
         
    elif low == 1:
        print("Harvesting Low")
        time.sleep(5)
        print("done")
                
    response = "finished " + message_str    
    mom.write(response.encode())

def get_to_wall():
    print("get to wall")
    
def go_home():
    print("I want to go home")
    
def outside_right():
    print("turn right")
    
def inside_left():
    print("yes its a left turn, it may not look like it but it's left.")

# Main function here

print("Started")
while True:
    if mom.any():
        message = b""
        while True:
            data = mom.read(1)
            if not data or data == b'\n':
                break
            message += data
        message_str = message.decode('utf-8').strip()
        
        print("Received message:", message_str, " from mom.")
        time.sleep(0.2)
        response = "starting " + message_str
        print(response)
        mom.write(response.encode())
   
        if   message_str == "harvest01":		# Harvest Low
            harvest(0, 1)
        elif message_str == "harvest10":		# Harvest High
            harvest(1, 0)
        elif message_str == "harvest11":		# Harvest Both High and Low
            harvest(1, 1)
        elif message_str == "get_to_wall":		# Starts from corner and needs to get within real sense range of the first wall
            get_to_wall()
        elif message_str == "outside_right":	# Is supposed to turn 180 degrees to the new row
            outside_right()
        elif message_str == "inside_left:":		# Is supposed to turn 180 degrees to opposite wall
            inside_left()
        elif message_str == "go_home":			# Is supposed to bring the robot to the final corner
            go_home()
        
        else:
            mom.write("bad send".encode())
            

        
        
        #switch
        
        # send complete
        
    time.sleep(0.1)
