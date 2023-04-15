#This file is the code for the wall folower changed into a class.

import controlers as ctrl
import numpy as np
import scipy.stats as stat

# Potential problems:
# Damping ratio needs to be raised
# rise time needs to be tuned
# maximum angle needs to be lowered.
#Navigation Parameters:
target = 0 #in inches. Will need to convert the camera units

#Controller Parameters:
t = .75 #Rise time (seconds)
z = .707#Damping ratio- The longer period between updating the controller the higher value this needs to be. For very small .707
sigma = 0.05 # Dirty Derivative value

#Saturation Limits:
vmax = 5 #in/s
vmin = 0 #in/s
ThetaMax = np.pi/2 -.2 #because we are using an observer, we can increase our maximum theta
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
    def __init__(self, sim = False):
        if(sim):
            self.WF = ctrl.PD2ndOrderADV(b0, a1, a0,              #Coupled system transfer function variables
                                        t, z, sigma, .01,    #Controller parameters
                                        Dmin, Dmax               #output saturation
                                        )
        else:
            self.WF = ctrl.PD2ndOrderADV(b0, a1, a0,              #Coupled system transfer function variables
                                            t, z, sigma, ctrl.live,    #Controller parameters
                                            Dmin, Dmax               #output saturation
                                            )
            
    def update_sim(self, theta, y, Ts):
        self.WF.Tstep = Ts #Set time step to a custom value

        #Run controller to determine turn rate:
        d = self.WF.update(target, y)
        
        #System coupling:
        if theta >= ThetaMax:
            if d > 0: #allow the robot to go back
                d = 0 #Don't go past theta max
                v = vmax
            else:
                v = vmax - (vmax-vmin)*(abs(d)/Dmax)
        elif theta <= ThetaMin:
            if d < 0: #allow the robot to go back
                d = 0 #Don't go past theta max
                v = vmax
            else:
                v = vmax - (vmax-vmin)*(abs(d)/Dmax)
        else:
            v = vmax - (vmax-vmin)*(abs(d)/Dmax)


        dtheta = d/L #Convert to rad/s

        return [v, dtheta]

    def update(self, theta, y):
        d = self.update(target, y)

        #System coupling:
        if theta >= ThetaMax:
            if d > 0: #allow the robot to go back
                d = 0 #Don't go past theta max
                v = vmax
            else:
                v = vmax - (vmax-vmin)*(abs(d)/Dmax)
        elif theta <= ThetaMin:
            if d < 0: #allow the robot to go back
                d = 0 #Don't go past theta max
                v = vmax
            else:
                v = vmax - (vmax-vmin)*(abs(d)/Dmax)
        else:
            v = vmax - (vmax-vmin)*(abs(d)/Dmax)


        dtheta = d/L #Convert differential to rad/s   

        return [v, dtheta] 
    
    # def update(self, X, Z):
    #     #Take in the relevant point cloud values and ouput the controlls
    #     #Depending on the speed the camera can run, this may need to be split into two
    #     slope, y, r, p, se = stat.linregress(X,Z)
    #     r = r**2

    #     #Calculate theta value for use in the controller:
    #     theta = np.arctan(slope)

    #     d = self.WF.update(target,y)
    # # print(d)
    # #Determine speed based on turn rate
    # #This may need to be updated to be less abrupt.
    #     if theta >= ThetaMax:
    #         v = vmax
    #         if d > 0: #allow the robot to go back
    #             d = 0 #Don't go past theta max
    #     elif theta <= ThetaMin:
    #         v = vmax
    #         if d < 0: #allow the robot to turn back
    #             d = 0 #Don't go past theta min
    #     else:
    #         v = vmax - (vmax-vmin)*(abs(d)/Dmax)


    #     dtheta = d/L #Convert to rad/s
        

    #     #return the controller parameters and the r**2 value
    #     return [v.item(0), dtheta, r]




class position_observer:
    def __init__(self, x = 0, y = 0, theta = 0): #arguments are initial position
        self.state = np.array([[x],
                               [y],
                               [theta]])
        
    def update_DR(self, v, d, Ts): #Dead reaconing
        #Theta will need to be corrected from the controller output based on which way the robot is facing.
        x = self.state.item(0)
        y = self.state.item(1)
        theta = self.state.item(2)
        v = np.array([v]).item(0)
        d = np.array([d]).item(0)
        #Calculate the difference based on the previous state
        #Because the system is highly non-linear, and the system must operate in nearly all 360deg, we will not linearize
        dist = np.array([[np.cos(theta)*v],
                         [np.sin(theta)*v],
                         [d]])
        dist  *= Ts #multiply by the elapsed time to get changes

        self.state +=dist #Add the movement to the state

    def correct_x(self, x, confidence):
        self.state[0] += confidence*(x - self.state[0])

    def correct_y(self, y, confidence):
        self.state[1] += confidence*(y - self.state[1])

    def correct_theta(self, theta, confidence):
        self.state[2] += confidence*(theta - self.state[2])
    
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
