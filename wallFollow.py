# wallFollow.py
# This file contains code to take inputs from the realsense camera and generate outputs for the stepper
# motors based on a controller
# Author:           Josh Chapman
# Created:          Feb 22, 2023

# Complete:
    # initialize realsense camera and controller
    # Generate a point cloud from the realsense
    # Find the wall based on a linear regression of the point cloud
        # commands in velocity (inches) and angular velocity (probably radians)
# To Do:
    # Generate a mask based on wall color/area of interest
    # Determine behavior at failure 
        # (IE no data from the camera, or the camera is too close to the wall)
    # Detect wall edge


#Standard libraries
import cv2
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
#time library for identifying the places where time is being lost
import time
from Hardware import Filter as F

#custom libraries:
import controlers as ctr
import Hardware.RealSense as rs

#Initialize camera
cam = rs.RSCam(Range= "Short")

#Robot physical parameters:
L = 12 #Distance between wheels

#Navigation parameters
target = .2 #Desired distance from the wall

#Controller Parameters:
t = 1  #Desired Rise Time of the system
#Starting with a larger rise time for safety
ThetaMax = np.pi/6 
ThetaMin = -1*ThetaMax
#Starting with a smaller max angle to make sure the camera can still see the wall.

vmax = 5 #in/s
vmin = 0 #in/s

#Starting with a smaller max angle to test 
z = .707

Dmax = 2*vmax #difference in speed between the two wheels
Dmin = -1*Dmax
sigma = .01


#Transfer Function Variables
b0 = vmax/L
a0 = a1 = 0

#initialize controller:
WF = ctr.PD2ndOrderADV(b0, a1, a0,              #Coupled system transfer function variables
                       t, z, sigma, ctr.live,    #Controller parameters
                       Dmin, Dmax               #output saturation
                       )

#initial states
d = 0.
v = 0.

#Follow the wall:
#This will output to the pico
# Outputs: Velocity, dtheta

# plt.ion()
plt.title("looking down")
plt.xlim([-.3,.3])
plt.ylim([0, .6])

while(1): #will add an exit condition later.
    #  Initialize variables that we will need later.
    slope = 0.
    y = 0.
    X = np.array([1])
    Y = np.array([1])
    Z = np.array([1])
    while(1): #Change to a for loop to prevent getting stuck

        # This try function is because the realsense camera was feeding bad data to the wall follower, to the point it was causing crashes.
        # If this fails don't update the observer. 
        # We should still be able to read the locations of the bolls from the camera.
        #Potential for fatal error:
        ##### Goes out of range of the camera and is unable to update the observer. May cause the robot to crash.   
        # try: 
        if(True):
                 
            told = time.ctime()
            cam.get_frames()#update camera data
            print("Have new frame")
            cam.color_image =  cv2.blur(cam.color_image, [20,20])
            cv2.imshow("Blured image and depth image", cam.usr_image())
            #Blur the image to get a better filter result
            
            tnew = time.ctime()
            # print("time to get frames ", tnew-told)
            
            # Will generate a mask that filters things out later.
            lock, unripe_bolls, ripe_bolls, mask1 = F.Harvest_Filter(cam.color_image)
            # mask1 = cv2.inRange(cam.color_image, F.wall_low, F.wall_high)
            print(mask1)
            cv2.imshow("mask", mask1)
            depthMask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data

            # Generate the point cloud:
            told = time.ctime()
            pc = cam.FilteredCloud(mask1)
            tnew = time.ctime()
            # print("time to generate the point cloud:  ", tnew-told)

        
        
            #linear regression:
        
            # Analysis of the data started failing after implementing the filters. Set to keep trying to get a good frame until it works.
            #analyze the point cloud:
            #Get the points in the x-z plane
            X = np.transpose(pc[:,0]) #first column of the point cloud
            Z = np.transpose(pc[:,2]) #third column of the point cloud
            slope, y, r, p, se = stat.linregress(X, Z)
            r = r**2
        # except:
        #     print("bad data")
        # finally:
        #     break

    

    # print(slope)
    #Find the angle and run the controller.
    theta = np.arctan(slope)
    # print(y)
    d = WF.update(target,y)
    # print(d)
    #Determine speed based on turn rate
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

    #Use r value to tell if there is a corner

    output = [v,dtheta]


    #Visualization code:
    
    fig = plt.figure(1)
    plt.annotate("V = " + str(v) + "\nd = " + str(d), [-.3,.6])
    # print(output)
    # print(v)
    length = np.arange(-.3,.4,.1)
    wall = slope*length + y
    tar = np.ones(np.shape(length))*target
    
    plt.xlim([-.3,.3])
    plt.ylim([0, .6])
    plt.scatter(X,Z)
    plt.plot(length, wall)
    plt.plot(length, tar)
    plt.draw()
    plt.pause(0.01)
    plt.cla()
