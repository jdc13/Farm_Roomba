# Pi Coms for Uart Transmission
# 5/10/2023

import serial
import time

#with open('/boot/config.txt', 'a') as f:
 #   f.write('enable_uart=1\n')
  #  f.write('dtoverlay-uart3\n')
  
    # There is also the following option that should connect as well, the issue
    # is that I'm unsure what it does differently. I'm sure that what currently
    # is in place will always want pins 8 and 10
    # serial.Serial('/dev/ttyS0', 9600) 
pico  = serial.Serial('/dev/serial0', 9600)
esp32 = serial.Serial('/dev/serial1', 9600)

run = True
color = "green"
while run == True:
    # Send colors over serialport to be interpretted
    if color == "green":
        pico.write(b"green")
        esp32.write(b"green")
        print("GREEN written to both boards")
        time.sleep(1) 
        pico_msg = pico.readline().decode().strip()
        if pico_msg != "green received":
            print("brian screwed up")
            run = False
            
        print("success!")
        color = "yellow"
        time.sleep(1)
    
    if color == "yellow":
        pico.write(b"yellow")
        esp32.write(b"yellow")
        print("YELLOW written to both boards")
        time.sleep(1)
        if pico_msg != "yellow received":
            print("brian screwed up")
            run = False

        print("success!")
        color = red
        time.sleep(1)
    
    if color == "red":
        pico.write(b"red")
        esp32.write(b"red")
        print("RED written to both boards")
        time.sleep(1)
        if pico_msg != "red received":
            print("brian screwed up")
            run = False

        print("success!")
        color = "green"
        time.sleep(1)
    
    
