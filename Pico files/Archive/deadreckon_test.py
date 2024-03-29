# Carters code to test dead reckoning

from machine import Pin, PWM
from time import sleep

class Driving_control:

    def __init__(self):

​

        self.leftPWM = PWM(Pin(15))

        self.rightPWM = PWM(Pin(19))

        self.leftDir = Pin(14, Pin.OUT)

        self.rightDir = Pin(18, Pin.OUT)

​

        self.baseSpeed = 300

​

        self.deg_90 = 1285

        

        self.delay = .5

​

        self.leftPWM.freq(200)

        self.rightPWM.freq(200)

        self.leftPWM.duty_u16(0)

        self.rightPWM.duty_u16(0)

        self.leftDir.value(0)

        self.rightDir.value(0)

        

        self.steps = 0

        self.Int_Pin= Pin(22, Pin.IN, Pin.PULL_DOWN)

        self.Int_Pin.irq(trigger= Pin.IRQ_FALLING, handler= self.Step_Counter)

​

    def Step_Counter(self, pin):

        self.Int_Pin.irq(handler=None)

        self.steps = self.steps + 1

        self.Int_Pin.irq(handler=self.Step_Counter)    

​

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

    drive_commands= Driving_control()

    

    #drive_commands.Find_corner()

    #drive_commands.DriveStraight(1100, dir="b")

    #drive_commands.DriveStraight(1100)

    #drive_commands.Left_corner()

    

    '''

    # Full Course Navigation Sequence

    drive_commands.Find_wall()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Right_corner()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Left_corner()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Right_corner()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Left_corner()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Right_corner()

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.DriveStraight(730)

    drive_commands.Find_corner()

    '''

    drive_commands.Stop()

    sleep(1)

    break

