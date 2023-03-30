#This file is the code for the wall folower changed into a class.

import controlers as ctrl
import numpy as np
import scipy.stats as stat


#Navigation Parameters:
target = 0.2 #Units that the camera uses

#Controller Parameters:
t = 1 #Rise time (seconds)
z = 0.707 #Damping ratio
sigma = 0.01 # Dirty Derivative value

#Saturation Limits:
vmax = 5 #in/s
vmin = 0 #in/s
ThetaMax = np.pi/6 
ThetaMin = -1*ThetaMax
Dmax = 2*vmax #difference in speed between the two wheels
Dmin = -1*Dmax

#Physical System Parameters:
L = 12 #Distance between wheels

#Coupled system transfer function:
#_________b0__________
#  s**2 + a1*s + a0
b0 = vmax/L
a0 = a1 = 0

class WallFollow:
    def __init__(self):
        self.WF = ctrl.PD2ndOrderADV(b0, a1, a0,              #Coupled system transfer function variables
                                     t, z, sigma, ctrl.live,    #Controller parameters
                                     Dmin, Dmax               #output saturation
                                     )
        
    def update(self, X, Z):
        #Take in the relevant point cloud values and ouput the controlls
        #Depending on the speed the camera can run, this may need to be split into two
        slope, y, r, p, se = stat.linregress(X,Z)
        r = r**2

        #Calculate theta value for use in the controller:
        theta = np.arctan(slope)

        d = self.WF.update(target,y)
    # print(d)
    #Determine speed based on turn rate
    #This may need to be updated to be less abrupt.
        if theta >= ThetaMax:
            v = vmax
            if d > 0: #allow the robot to go back
                d = 0 #Don't go past theta max
        elif theta <= ThetaMin:
            v = vmax
            if d < 0: #allow the robot to turn back
                d = 0 #Don't go past theta min
        else:
            v = vmax - (vmax-vmin)*(abs(d)/Dmax)


        dtheta = d/L #Convert to rad/s
        

        #return the controller parameters and the r**2 value
        return [v, dtheta, r]

