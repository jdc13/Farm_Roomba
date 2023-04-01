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




class position_observer:
    def __init__(self, x = 0, y = 0, theta = 0): #arguments are initial position
        self.state = np.array([[x],
                               [y],
                               [theta]])
        
    def update_DR(self, v, d, steps): #Dead reaconing
        #Theta will need to be corrected from the controller output based on which way the robot is facing.
        x = self.state.item(0)
        y = self.state.item(1)
        theta = self.state.item(2)

        #Calculate the difference based on the previous state
        dist = np.array([[np.sin(theta)*v],
                         [np.cos(theta)*v],
                         [d]])
        dist  *= steps #multiply by the number of steps to get the distance traveled

        self.state +=dist #Add the movement to the state

    def update_MXT(self, xm, tm): #update the x and the theta based on the distance from the wall
        # measured values for x and theta will need to be adjusted for which wall the robot is on.
        
        measured = np.array([[xm],
                             [0],
                             [tm]])
        C = np.array([[1,0,0],
                      [0,0,0],
                      [0,0,1]])
        
        self.state += .75*(measured - C @ self.state)
        

    def update_MY(self, ym): #update the y location
        measured = np.array([[0],
                             [ym],
                             [0]])
        C = np.array([[0,0,0],
                      [0,1,0],
                      [0,0,0]])
        
        self.state += .75*(measured - C @ self.state)
