# Send and receive Raspberry Pi
# Brian Jones 6/6/2023
# The code here is to be used for dead
# reckoning functions in order for the pi
# to know when a task has been received, as
# well as been completed by the pico

import time
import serial

# Initializes pins for uart coms to be used, 9600 baud rate
pico = serial.Serial('/dev/serial0', 9600, timeout = 1)

# Wait for start starts a timer for 5 seconds where the pico has a limited time to respond
# or it will return an error to try and resend the command. If proper message comes back
# through the uart  it will pass a success message.
def wait_for_start(timeout_duration, command):
    print("\nNow looking for the start signal...")

    start_time = time.time()
    while (time.time() - start_time) < timeout_duration:
        # in_waiting - Return the number of bytes in the receive buffer
        if pico.in_waiting > 0: # if there are bytes to read in the recieve buffer
            message = pico.readline().decode().strip()# read in byte array from pico and convert into string
            # decode - converts bytearray into string - python method
            # strip - removes spaces at the beginning and end of a string - string method
            
            print("recieved message: ", message)
            
            if message == "starting " + command:# if message is "starting " return success
                print("pico started correct command!")
                return "success"
            elif message == "bad send":# if an unknown or unfamiliar command is sent, return bad send
                print("unknown command was sent.")
                return "bad send"
            elif message != "starting " + command:# otherwise return error
                # could this just be an else statement?
                print("pico messaged the wrong message!", message)
                return "error"
                    
    if (time.time() - start_time) >= timeout_duration:# is there is no message returned within time_duration, return error
        print("Error: timeout of message.")
        return "error"
    
    
def wait_for_completion(timeout_duration, command):
    print("\nNow looking for completion signal...")
    start_time = time.time()
    while (time.time() - start_time) < timeout_duration:
        if pico.in_waiting > 0:
            message = pico.readline().decode().strip()
            print("recieved message: ", message)
            
            if message == "completed " + command:# if command is completed, return success
                print("easy dub, task was completed succesfully.")
                return "success"
            elif message != "completed " + command:# if command is not commpleted, return error
                print("reached too close to the sun here, didn't work")
                return "error"
            
    if (time.time() - start_time) >= timeout_duration:#timeout error
        print("Error: timeout of message.")
        return "error"
                
            
            
# Send command is the one stop destination to send a command to the pico. It will send the command
# from input and the pico must add 'starting ' + command to ensure that the  message was received properly.
# Afterwards send command will wait for completion which I will choose a arbitrary timeout time
# atm because I am unsure how long any command will take, so I chose 10 seconds. Unfortunately while
# an error message is really useful for the wait_for_start because the error is most likely bad coms,
# theres no easy way to fix an error for wait_for_completion as the command has run its course already. or
# at least that I know of so I am simply putting a print error statement unless we find something better.
# it could be possible to revert back to wall follow but without testing im unsure how effective it would
# be.
def send_command(command):
    pico.write(command.encode())# send the pico a command
    #encodes the string, using the specified encoding. If no encoding is specified, UTF-8 will be used. - python method
    print("Sent pico the command: ", command)# print out current action
    sent = wait_for_start(5, command) 
    error_count = 0
    if sent == "error":
        while error_count < 3: #if wiat for start retuns 3 errors
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
    
        
    
        
###############################
# Main
#
###############################

print("Starting my code.")
time.sleep(3)
success = False
command = input("Please enter a command: ")

success = send_command(command)
if success == True:
    print("Operation was sent and completed properly.")
elif success == False:
    print("Pico did not fully complete task.")
    
    
