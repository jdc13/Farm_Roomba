#This file should be run on startup. 
#It will illuminate the power button and shut down the raspberry pi when the button is pressed.
#Place this file in the home directory

# Instructions on final setup:
# https://www.instructables.com/Simple-Raspberry-Pi-Shutdown-Button/

# Run these commands:
# sudo nano /etc/rc.local
# Add the following to the bottom just below the exit:
# python/home/<usr>/shutdown.py




import RPi.GPIO as gpio
import os
from time import sleep

# Terminal command to install gpio library if it isn't already:
#$ sudo apt-get install python-rpi.gpio python3-rpi.gpio

gpio.setmode(gpio.BOARD)

#pins for power and LED
powerButton = 5
LED = 6

#Set up power button pin
gpio.setup(powerButton, gpio.IN, pull_up_down=gpio.PUD_UP)

#Set up LED indicator pin to be an output and turned on
gpio.setup(LED, gpio.OUT, initial = gpio.HIGH)

#wait for the button press:
gpio.wait_for_edge(powerButton, gpio.FALLING)

#blink the LED a afew times to show that the button has been pressed and that shutoff has been initiated
for i in range(1,4):
    gpio.output(LED, gpio.LOW)
    sleep(.25)
    gpio.output(LED, gpio.HIGH)

#send shutdown command to system:
os.system("sudo shutdown -h now")

