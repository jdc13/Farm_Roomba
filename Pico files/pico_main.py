from machine import Pin, PWM
from time import sleep

leftPWM = PWM(Pin(21))
rightPWM = PWM(Pin(11))

leftDir = Pin(26, Pin.OUT)
rightDir = Pin(15, Pin.OUT)

baseSpeed = 300

leftPWM.freq(200)
rightPWM.freq(200)
leftPWM.duty_u16(0)
rightPWM.duty_u16(0)
leftDir.value(0)
rightDir.value(0)


def DriveStraight(speed=baseSpeed, dir="f"):
    leftPWM.freq(speed)
    rightPWM.freq(speed)
    leftPWM.duty_u16(10000) #10,000/65,536
    rightPWM.duty_u16(10000)
    if dir is "f":
        leftDir.value(0)
        rightDir.value(1)
    elif dir is 'b':
        leftDir.value(1)
        rightDir.value(0)
        

def Turn(speed=baseSpeed, dir='r'):
    leftPWM.freq(speed)
    rightPWM.freq(speed)
    leftPWM.duty_u16(10000)
    rightPWM.duty_u16(10000)
    if dir is "l":
        leftDir.value(1)
        rightDir.value(1)
    elif dir is 'r':
        leftDir.value(0)
        rightDir.value(0)
        
def Stop():
    leftPWM.duty_u16(0)
    rightPWM.duty_u16(0)

 
def Step_Counter(pin):
    global steps
    Int_Pin.irq(handler=None)
    steps = steps + 1
    Int_Pin.irq(handler=Step_Counter)    
        
Int_Pin= Pin(16, Pin.IN, Pin.PULL_DOWN)

Int_Pin.irq(trigger= Pin.IRQ_FALLING, handler= Step_Counter)

steps=0
while True:

    
    #while steps<=1000:
    #    DriveStraight()
    
    while steps<=1290:
        Turn(dir='r')
    Stop()
    steps=0
    sleep(.5)
    while steps<=1400:
        DriveStraight()
    Stop()
    steps=0
    sleep(.5)
    while steps<=1290:
        Turn(dir='r')
    Stop()
    steps=0
    sleep(.5)
    while steps<=1400:
        DriveStraight()
    Stop()
    steps=0
    sleep(.5)
    #Stop()
    #break
