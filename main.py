#This file will be the base file that calls all other functions. 
# from Hardware import Hardware as dev
import numpy as np
import pandas as pd
import cv2
import scipy.stats as stat

import wallFollow_class as WF
import Hardware.RealSense as RS



#States
class state:
    
    #Finite States:
    currentState = 0

    #possible states:
    init = 0            #initialize hardware and move to the proper location
    follow_wall = 1     #Follow the wall
    map = 2             #map located boll
    harvest = 3         #harvest boll(s)
    corner_in = 4       #turn arround inside a row
    corner_out = 5      #turn arround a wall
    finish = 6          #Move from the end of the last row to the final location. Store the map to a file

#Location tracking
#I moved these out of states so that states is dedicated to the state machine
# loc_phys = np.zeros((1,2), float) #X and Y coordinates
location = WF.position_observer(6, -6) #Initialize location observer with the robot in the corner (center of the robot offset by 6")
loc_map = np.zeros((1,2), int) # row and plant location

#Controllers:
wallFollow = WF.WallFollow()

#hardware
cam = RS.RSCam(Range= "Short")

#initialize a dataframe of 0s the size of the map
#6 rows, 9 plants, only 3 rows are relevant
map = pd.DataFrame(np.zeros((3,9)), 
                   index=[2,4,6], 
                   columns=['P1','P2','P3','P4','P5','P6','P7','P8','P9'])

# add switch statement

## init
# set up
# wallfollow

xobs = location.state.item(0)
yobs =location.state.item(1)
thetaobs = location.state.item(2)
v, dtheta = wallFollow.update(thetaobs, yobs)
location.update_DR(v, dtheta, wallFollow.WF.Ts)


#If X is within an error margin of the harvest stop:
#Change state to harvest
#else if x within an error margin of the end of the wall
#Change state to corner based on location





## Harvest
# stop at bol
# Collect image
cam.get_frames()
#Generate masks to filter data- this will need to be done for the wall, ripe bols and unripe bolls
mask1 = np.ones(np.shape(cam.depth_image)) * 255
depthMask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data


pc = cam.FilteredCloud(mask1)

#Find wall data:
X = np.transpose(pc[:,0]) #first column of the point cloud
Z = np.transpose(pc[:,2]) #third column of the point cloud
#linear regression:
slope, y_m, r, p, se = stat.linregress(X, Z)
r = r**2
theta_m = np.arctan(slope)



location.correct_x(x measurement, .5)
location.correct_y(y_m, .5)
location.correct_theta(theta_m, .75)
# fine tune
# color functions
# call harvest(pass bolLoc, ripeLoc)
# map
# bolCounter++
# return done
#   status pin to return done
# WallFollow

## RightCorner
# turn corner
# reset bol counter
# return done
# WallFollow

## LeftCorner
# turn corner
# reset bol counter
# return done
# WallFollow

##end
#maybe go back to start?

## sample
#based on the bol counter, decide next action

#export CSV file in the prescribed format:
map.to_csv("map.csv", index_label="Row:")