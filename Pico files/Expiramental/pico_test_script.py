from machine import Pin, PWM
from time import sleep
# Imports for I2C
import board
import busio

leftPWM = PWM(Pin(21))
rightPWM = PWM(Pin(11))

#Constants
R = 2 #cm, wheel radius
L = 10; # Robot wheelbase
steps_per_rev = 2045 # stepper motor resolution
max_speed = 1 # max velocity that can be handled by the steppers
max_startup_speed = 0.5 # highest velocity that won't stall the motors
duty_percent = 50

# Pin interrupts to count steps
def Step_Counter(pin):
    global steps
    Int_Pin.irq(handler=None)
    steps = steps + 1
    Int_Pin.irq(handler=Step_Counter)
Int_Pin= Pin(16, Pin.IN, Pin.PULL_DOWN)
Int_Pin.irq(trigger= Pin.IRQ_FALLING, handler= Step_Counter)

# I2C Setup
i2c = busio.I2C(sda=Pin(0), scl=Pin(1))
#masterAddress = 0x55
devices = i2c.scan()


while True:

    try:
        data = read_i2c_block_data(masterAddress, 0x00, 16)
        # Inputs
        v_comm = 0 # fix: read the I2C
        w_comm = 0 # fix: read the I2C

        # Calculations
        #deg_per_step = 360/steps_per_rev 
        #w_r_comm = (2*v_comm + L*w_comm)/(2*R) # rad/s
        #w_l_comm = (2*v_comm - L*w_comm)/(2*R)
        #freq_r_comm = 2*3.14159*w_r_comm # wheel ang. vel. in Hz
        #freq_l_comm = 2*3.14159*w_l_comm
        #ulse_freq_r = freq_r_comm * 360 / deg_per_step # Wheel rotation freq (Hz) = deg/step * 1rot/360deg * pulses/sec -> pulses/sec = wheel rot/s * 360 deg/rot / (deg/step)
        #pulse_freq_l = freq_l_comm * 360 / deg_per_step

        # Calculations condensed
        pulse_freq_r = 2 * 3.14159 * 360 * (360/steps_per_rev) * (2*v_comm + L*w_comm)/(2*R)
        pulse_freq_l = 2 * 3.14159 * 360 * (360/steps_per_rev) * (2*v_comm - L*w_comm)/(2*R)
        duty = (duty_percent/100)*65536 #convert duty cycle percent to u16 value

        # Motor Commands
        # Check for zero movement?
        rightPWM.freq(pulse_freq_r)
        leftPWM.freq(pulse_freq_l)
        rightPWM.duty_u16(duty)
        leftPWM.duty_u16(duty)

        # Count Steps??
        # Not sure how we do this in velocity control, are ew just logging all steps and every time a command is changed, or are we not doing anything at all?

        command_recieved = False
    except:
        pass


# machine is exclusive to MicroPython, not CircuitPython!
# Might need to redo PWM using pwmio module? Need to check syntax
# Need to use busio for I2C (maybe could use board.I2C, but not sure this will work, so stick to busio for now)

#### Simple I2C Example #####
# Written in circuitpython, with Pico as master; need to make sure to use Thonny package manager to get right packages
'''from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

oled.text("Tom's Hardware", 0, 0)
oled.show()'''

    
    

