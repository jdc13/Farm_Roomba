# Send and receive Raspberry Pi
# Brian Jones 6/6/2023
# The code here is to be used for dead
# reckoning functions in order for the pi
# to know when a task has been received, as
# well as been completed by the pico

import time
import serial

# Initializes pins for uart coms to be used, 9600 baud rate
pico = serial.Serial('/dev/serial0', 9600)

start_loop = True
counter = 0

while start_loop == True:
    if counter == 0:
        # Sends command
        pico.write(b"harvest01")
        print("Sent pico 'harvest01'")
        
        # Looks to see if command has been received
        time.sleep(0.1)
        print("hello")
        message = pico.readline().decode().strip()
        print(message)
        if message == "starting harvest01":
            print("Pico has received my message 'harvest01'!")
        else:
            print ("error, bad send brian")
            
        # Looks to see if command has been completed

        message = pico.readline().decode.strip()
        if message == "finished harvest01":
            print("Pico has completed my message 'harvest01'!")
        else:
            print ("error, bad send brian")
        
        counter = counter + 1
        
        
    if counter == 1:
        # Sends command
        pico.write(b"harvest10")
        print("Sent pico 'harvest10'")
        
        # Looks to see if command has been received
        pico_msg = pico.readline().decode().strip()
        if pico_msg == "starting harvest10":
            print("Pico has received my message 'harvest10'!")
        else:
            print ("error, bad send brian")
            
        # Looks to see if command has been completed
        pico_msg = pico.readline().decode.strip()
        if pico_msg == "finished harvest10":
            print("Pico has completed my message 'harvest10'!")
        else:
            print ("error, bad send brian")
        
        counter = counter + 1
        
    if counter == 2:
        # Sends command
        pico.write(b"harvest11")
        print("Sent pico 'harvest11'")
        
        # Looks to see if command has been received
        pico_msg = pico.readline().decode().strip()
        if pico_msg == "starting harvest11":
            print("Pico has received my message 'harvest11'!")
        else:
            print ("error, bad send brian")
            
        # Looks to see if command has been completed
        pico_msg = pico.readline().decode.strip()
        if pico_msg == "finished harvest11":
            print("Pico has completed my message 'harvest11'!")
        else:
            print ("error, bad send brian")
        
        counter = counter + 1
        
        
        
