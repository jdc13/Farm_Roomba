from machine import Pin, PWM
from time import sleep

# Tuning: number of steps per unit
INCH = 143.76 # steps per inch
DEGREE = 14.4 # steps per degree

class Driving_control:
    def __init__(self):

        self.leftPWM = PWM(Pin(9))
        self.rightPWM = PWM(Pin(5))
        self.leftDir = Pin(8, Pin.OUT)
        self.rightDir = Pin(4, Pin.OUT)

        self.baseSpeed = 300

        self.deg_90 = 1285 #TODO: tune this

        self.delay = .5

        self.leftPWM.freq(200)
        self.rightPWM.freq(200)
        self.leftPWM.duty_u16(0)
        self.rightPWM.duty_u16(0)
        self.leftDir.value(0)
        self.rightDir.value(0)
        
        self.steps = 0
        self.Int_Pin= Pin(15, Pin.IN, Pin.PULL_DOWN) # creat a pin object #must be pin 15
        self.Int_Pin.irq(trigger= Pin.IRQ_FALLING, handler= self.Step_Counter) #interupt triggers on falling edge and calls Step_Counter

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
        self.Turn(angle= 550, dir='l')
        self.DriveStraight(INCH * 11.75)
        
    def Find_corner(self):
        self.Arc(1980, dir = 'l')
        self.Turn(angle= 380, dir='r')
        self.DriveStraight(800)
        
    def Right_corner(self):
        self.DriveStraight(INCH * 11.75) # was 1600
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(INCH * 15.75) # was 3600
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(INCH * 11.75) # was 1600
        
    def Left_corner(self):
        self.DriveStraight(INCH * 6)
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(INCH * 3.5)
        self.Turn(self.deg_90, dir ='r')
        self.DriveStraight(INCH * 1.5)
        
while True:
    drive_commands= Driving_control()
    drive_commands.Left_corner()
    #drive_commands.DriveStraight(10000)
    drive_commands.Stop()
    sleep(1)
    break
