from machine import Pin, PWM
from time import sleep
import math

#143.76 steps per inch
INCH = 143.76
DEGREE = 14.4

class Driving_control:
    def __init__(self):

        self.leftPWM = PWM(Pin(15))
        self.rightPWM = PWM(Pin(19))
        self.leftDir = Pin(14, Pin.OUT)
        self.rightDir = Pin(18, Pin.OUT)

        self.baseSpeed = 300

        self.deg_90 = 1298 # carson used 1285, but math says 1298.42
        
        self.delay = .5

        self.leftPWM.freq(200)
        self.rightPWM.freq(200)
        self.leftPWM.duty_u16(0)
        self.rightPWM.duty_u16(0)
        self.leftDir.value(0)
        self.rightDir.value(0)
        
        self.steps = 0
        self.Int_Pin= Pin(22, Pin.IN, Pin.PULL_DOWN)
        self.Int_Pin.irq(trigger= Pin.IRQ_FALLING, handler= self.Step_Counter)

    def Step_Counter(self, pin):
        self.Int_Pin.irq(handler=None)
        self.steps = self.steps + 1
        self.Int_Pin.irq(handler=self.Step_Counter)    

    def DriveStraight(self, distance, speed= 300, dir="f"):
        while self.steps <= distance:
            if dir is "f":
                self.leftDir.value(1)
                self.rightDir.value(1)
            elif dir is 'b':
                self.leftDir.value(0)
                self.rightDir.value(0)
            self.leftPWM.freq(speed)
            self.rightPWM.freq(speed)
            self.leftPWM.duty_u16(10000) #10,000/65,536
            self.rightPWM.duty_u16(10000)
        self.Stop()
        self.steps=0
        sleep(self.delay)
        
    def Turn(self, angle, speed=300, dir='r'):
        while self.steps<=angle:
            if dir is "l":
                self.leftDir.value(0)
                self.rightDir.value(1)
            elif dir is 'r':
                self.leftDir.value(1)
                self.rightDir.value(0)
            self.leftPWM.freq(speed)
            self.rightPWM.freq(speed)
            self.leftPWM.duty_u16(10000)
            self.rightPWM.duty_u16(10000)
        self.Stop()
        self.steps=0
        sleep(self.delay)
        
    def Arc(self, angle, speed=300, dir='r'):
        while self.steps<=angle:
            self.leftDir.value(1)
            self.rightDir.value(1)
            if dir is "l":
                self.leftPWM.freq(200)
                self.rightPWM.freq(340)
            elif dir is 'r':
                self.leftPWM.freq(340)
                self.rightPWM.freq(200)
            self.leftPWM.duty_u16(10000)
            self.rightPWM.duty_u16(10000)
        self.Stop()
        self.steps=0
        sleep(self.delay)
            
    def Stop(self):
        self.leftPWM.duty_u16(0)
        self.rightPWM.duty_u16(0)
        
    def Find_wall(self):
        self.Arc(1700)
        self.Turn(angle= 585, dir='l')
        self.DriveStraight(1450)
        
    def Find_corner(self):
        self.Arc(1980, dir = 'l')
        self.Turn(angle= 380, dir='r')
        self.DriveStraight(800)
        
    def Right_corner(self):
        self.DriveStraight(1600)
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(3300) # 3600 is too long
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(1600)
        self.DriveStraight(1100)
        
    def Left_corner(self):
        self.DriveStraight(1600)
        self.Turn(self.deg_90*2, dir ='l')
        self.DriveStraight(1600)
        self.DriveStraight(1100)
        
# Main Loop for Pico-only testing: call whatever functions you want
while True:
    drive_commands = Driving_control()
    
    #drive_commands.Find_corner()
    #drive_commands.DriveStraight(1100, dir="b")
    #drive_commands.DriveStraight(1100)
    #drive_commands.Left_corner()
    dowel_steps = 1600
    
    
    # Adjust() function
    



#constants needs for the function
    theta_man = 30	# Roomba will always turn at a 30 degree angle for calculation purposes
    
    # X is measured distance of roomba to the wall.
    x_des = 5  # this is the desired distance from the wall, probably in inches
    x_max = 0.25
    x_min = 0.25
    
    # Measured angle in parralell to the wall. positive leans left,
    # negative will lean right in parallel to the wall
    theta_max = 1
    theta_min = -1
    
    # Measured dist to the next boll if it be off.
    y_min = -0.25
    y_max = 0.25
    
    # Variables ADjust() needs to receive from location.state((x), (y), theta))
    x_meas = 5
    y_meas = -4
    theta_meas = 0
    
    # If distance is greater than desired
    if x_meas > x_des + x_max:
        # calculate
        # stuff
        delta_x = x_meas - x_des
        forward_dist = delta_x / math.tan(math.radians(theta_man))       
        back_dist = forward_dist / math.cos(math.radians(theta_man))
        theta_turn = 14.4 * (theta_man - theta_meas)
        theta_man_turn = theta_man * 14.4
            
        # These commands are good to run the code in main of pico,
        # for the pi they will need to be changed to
        # send_command(cmd + steps), so for turn right it should be
        # send_command(righttheta_turn) AS A STRING!
        drive_commands.Turn(theta_turn, dir = 'l')
        drive_commands.DriveStraight(INCH*back_dist, dir = 'b')
        drive_commands.Turn(theta_man_turn, dir = 'r')
        drive_commands.DriveStraight(INCH*forward_dist, dir = 'f')
        drive_commands.Stop()

    #If the distance is less than desired        
    elif x_meas < x_des - x_min:
        # calculate
        # stuff
        delta_x = x_meas - x_des
        forward_dist = -delta_x / math.tan(math.radians(theta_man))
        back_dist = forward_dist / math.cos(math.radians(theta_man)) 
        theta_turn = DEGREE * (theta_man + theta_meas)
        theta_man_turn = theta_man * DEGREE
        
        # These commands are good to run the code in main of pico,
        # for the pi they will need to be changed to
        # send_command(cmd + steps), so for turn right it should be
        # send_command(righttheta_turn) AS A STRING!
        drive_commands.Turn(theta_turn, dir = 'r')
        drive_commands.DriveStraight(INCH*back_dist, dir = 'b')
        drive_commands.Turn(theta_man_turn, dir = 'l')
        drive_commands.DriveStraight(INCH*forward_dist, dir = 'f')
        drive_commands.Stop()
        
    # Will update the angle if roomba is more than a degree off either way.
    elif theta_meas < theta_min:
        drive_commands.Turn(-theta_meas * DEGREE, dir = 'l')
        drive_commands.Stop()
    elif theta_meas > theta_max:
        drive_commands.Turn(theta_meas * DEGREE, dir = 'r')
        drive_commands.Stop()

    #Updates Y distance after
    if y_meas > y_max:
        drive_commands.DriveStraight(INCH*y_meas, dir = 'b')
    elif y_meas < y_min:
        drive_commands.DriveStraight(INCH*-y_meas, dir = 'f')
