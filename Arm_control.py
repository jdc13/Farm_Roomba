from machine import Pin, PWM
import utime

class Armcontrol:
    def __init__(self):
        frequency= 150   #Please don't change the frequency
        self.PWM= 65534  #Don't change this number either
        self.speed =.001  #Tuning parameter for motion control
        self.delay =.004   #Tuning parameter for motion control
        self.delay_harvesting = 2  #delay for harvesting
        self.joint1 = PWM(Pin(19)) # Attach PWM object on a GPIO 19
        self.joint2 = PWM(Pin(20))
        self.joint3 = PWM(Pin(21))
        self.joint1.freq(frequency)
        self.joint2.freq(frequency)
        self.joint3.freq(frequency)

        #------------Angles Guide----------------
        # Servo motors are 270 degree servos
        # J1 is the Shoulder
        # J2 is the Elbow
        # J3 is the Wrist
        # J1-0 would be the base joist angle for J1
        # J#-L is the lower pre-harvest position
        # J#-LH is the lower harvesting position
        # J#-I is the intermediate harvesting position when harvesting both the lower and upper bulb
        # J#-U is the upper pre-harvest position
        # J#-UH is the upper harvesting position
        #----------------------------------------

        #------------Joint 1 Angles--------------
        
        # .06 is the small angle possible

        self.j1_0 = .23
        self.j1_L = .25
        self.j1_LH = .26
        self.j1_I = .21
        self.j1_U = .24
        self.j1_UH = .26

        #------------Joint 2 Angles--------------

        self.j2_0 = .226
        self.j2_L = .17
        self.j2_LH = .15
        self.j2_I = .19
        self.j2_U = .1
        self.j2_UH = .08

        #------------Joint 3 Angles--------------
        
        # .08 is the small angle before hitting the bracket
        # .31 is the largest angle before hitting the arm

        self.j3_0 = .31
        self.j3_L = .19
        self.j3_LH = .17
        self.j3_I = .2
        self.j3_U = .11
        self.j3_UH = .12
        
        
        #Write the motors to the start position and set the current angle 
        
        self.joint1.duty_u16(int(self.j1_0*self.PWM))
        self.joint2.duty_u16(int(self.j2_0*self.PWM))
        self.joint3.duty_u16(int(self.j3_0*self.PWM))
        utime.sleep(2)
        
        self.current_ang1 = self.j1_0
        self.current_ang2 = self.j2_0
        self.current_ang3 = self.j3_0
        self.state = 0

    def harvest_time(self, ripe=[0, 0]):
        picking = 0
        while picking == 0:
            if self.state == 0:
                if ripe[0] == 0:
                    self.pick_lower_bulb()
                    self.state= 1
                elif ripe[1] == 0:
                    self.pick_upper_bulb()
                    self.state = 3
                else:
                    self.base_pose()
                    self.state = 0
                    picking = 1

            elif self.state == 1:
                if ripe[1] == 0:
                    self.intermediate_pose()
                    self.state = 2
                else:
                    self.base_pose()
                    self.state = 0
                    picking = 1
            
            elif self.state == 2:
                if ripe[1] == 0:
                    self.pick_upper_bulb()
                    self.state = 3

            elif self.state == 3:
                self.base_pose()
                self.state = 0
                picking = 1

        return picking
            
    def pick_lower_bulb(self):
        picking = 0
        while picking == 0:
            self.move(self.j1_L, self.j2_L, self.j3_L)
            utime.sleep(.5)
            self.move(self.j1_LH, self.j2_LH, self.j3_LH)
            utime.sleep(self.delay_harvesting)
            picking = 1
            
    def pick_upper_bulb(self):
        picking = 0
        while picking == 0:
            self.move(self.j1_U, self.j2_U, self.j3_U)
            utime.sleep(.5)
            self.move(self.j1_UH, self.j2_UH, self.j3_UH)
            utime.sleep(self.delay_harvesting)
            picking = 1

    def base_pose(self):
        picking = 0
        while picking == 0:
            self.move(self.j1_0, self.j2_0, self.j3_0)
            picking = 1

    def intermediate_pose(self):
        picking = 0
        while picking == 0:
            self.move(self.j1_I, self.j2_I, self.j3_I)
            picking = 1

    def move(self, des_angle1, des_angle2, des_angle3):
        moving1 = 0
        moving2 = 0
        moving3 = 0
        while moving1 != 1 or moving2 != 1 or moving3 != 1:
            if self.current_ang1 < des_angle1:
                angle = int((self.current_ang1+self.speed)*self.PWM)
                self.joint1.duty_u16(angle)
                self.current_ang1= round(self.current_ang1+self.speed,3)
                utime.sleep(self.delay)
            elif self.current_ang1 > des_angle1:
                angle = int((self.current_ang1-self.speed)*self.PWM)
                self.joint1.duty_u16(angle)
                self.current_ang1= round(self.current_ang1-self.speed,3)
                utime.sleep(self.delay)
            elif self.current_ang1 == des_angle1:
                angle = int(self.current_ang1*self.PWM)
                self.joint1.duty_u16(angle)
                self.current_ang1 = des_angle1
                utime.sleep(self.delay)
                moving1 = 1
            
            if self.current_ang2 < des_angle2:
                angle = int((self.current_ang2+self.speed)*self.PWM)
                self.joint2.duty_u16(angle)
                self.current_ang2= round(self.current_ang2+self.speed,3)
                utime.sleep(self.delay)
            elif self.current_ang2 > des_angle2:
                angle = int((self.current_ang2-self.speed)*self.PWM)
                self.joint2.duty_u16(angle)
                self.current_ang2= round(self.current_ang2-self.speed,3)
                utime.sleep(self.delay)
            elif self.current_ang2 == des_angle2:
                angle = int(self.current_ang2*self.PWM)
                self.joint2.duty_u16(angle)
                self.current_ang2 = des_angle2
                utime.sleep(self.delay)
                moving2 = 1

            if self.current_ang3 < des_angle3:
                angle = int((self.current_ang3+self.speed)*self.PWM)
                self.joint3.duty_u16(angle)
                self.current_ang3= round(self.current_ang3+self.speed, 3)
                utime.sleep(self.delay)
            elif self.current_ang3 > des_angle3:
                angle = int((self.current_ang3-self.speed)*self.PWM)
                self.joint3.duty_u16(angle)
                self.current_ang3= round(self.current_ang3-self.speed, 3)
                utime.sleep(self.delay)
            elif self.current_ang3 == des_angle3:
                angle = int(self.current_ang3*self.PWM)
                self.joint3.duty_u16(angle)
                self.current_ang3 = des_angle3
                utime.sleep(self.delay)
                moving3 = 1
        return print("You made it!")
            
            
if __name__ == "__main__":
    arm= Armcontrol()
    arm.harvest_time(ripe=[0,0])
    utime.sleep(2)
    arm.harvest_time(ripe=[1,0])
    utime.sleep(2)
    arm.harvest_time(ripe=[0,1])
        
        