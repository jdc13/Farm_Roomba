#This file will be the base file that calls all other functions. 
# from Hardware import Hardware as dev
import numpy as np
import pandas as pd
import cv2
import scipy.stats as stat
import time

import wallFollow_class as WF
import Hardware.RealSense as RS
import Hardware.Filter as Filter



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
# I moved these out of states so that states is dedicated to the state machine
location = WF.position_observer(6, -6) #Initialize location observer with the robot in the corner (center of the robot offset by 6")
loc_map = np.zeros((1,2), int) # row and plant location

#The following need to be determined by looking at the scale map
boll_dist = 6 #Distance between bolls Set so that next boll is in field of view
expected_boll = 3 #location of next expected boll
rowbnd_max = 48
rowbnd_min = 24


#Controllers:
wallFollow = WF.WallFollow()

#hardware
cam = RS.RSCam(Range= "Short")
cam.get_frames() #Reject first frame (it's really dark.)

#initialize a dataframe of 0s the size of the map
#6 rows, 9 plants, only 3 rows are relevant
map = pd.DataFrame(np.zeros((3,9)), 
                   index=[2,4,6], 
                   columns=['P1','P2','P3','P4','P5','P6','P7','P8','P9'])

# add switch statement

# add switch statement
state = 'init'

bollCounter = 0
rowCounter = 0

while(1==1):
    match state:
        case 'init':
            # SetUp() This case is more a place holder for everything above the while loop. 
            location.time_old = time.time()
            state = 'wallfollow'
            ## init
            # set up
            # wallfollow

        case 'wallfollow':
            #tuple for the motor commands
            
            #gets new motoer cmnds
            
            [v,dtheta] = wallFollow.update(location.state[1],location.state[2]) #need to correct angle on rows where the robot is driving the other way.
            #update motor commands
            UpdateMotors(motorCmnds)



            now = time.time()
            Ts = now-location.time_old
            location.time_old = now
            location.update_DR(v,dtheta,Ts) #update location observer






            #State change triggers:
            if(location.state[0] > rowbnd_max):
                expected_boll -= boll_dist #Step back the expected boll location
                rowCounter += 1 #increment row
                bollCounter = 1 #reset boll
                state = "corner_in"
                 
            elif(location.state[0] < rowbnd_min):
                expected_boll += boll_dist
                rowCounter += 1 #increment row
                bollCounter = 1 #reset boll
                state = "corner_out"

            elif(
                (rowCounter % 2 == 1 and location.state[0] > expected_boll)
                or
                (rowCounter % 2 ==0 and location.state[0] < expected_boll)
                ):
                bollCounter +=1 #increment boll
                UpdateMotors(stop)
                state = "harvest"
                
            # state = Sample(bulbCounter,rowCounter)
            ## wallfollow
            # update motors
            # sample
            # if Harvest
            #   bool isAtBol (returns when we think we are at a bol
            #   Harvest

        case 'harvest':
            ## Harvest
            #Variables that will be accessed outside of their scope:
            slope = 0.
            y = 0.
            X = np.array([1])
            Y = np.array([1])
            Z = np.array([1])
            lock = 0
            unripe_bolls = 0
            ripe_bolls = 0

            for randomcounter in range(10): #Try to get 10 images. If it fails don't update the observer.
                try:# allows for errors
                    cam.get_frames() #update camera data

                    #smooth the image for better processing:
                    cam.color_image = cv2.blur(cam.color_image, [10,10])
                    kernel = np.array([[-1,-1,-1],
                                       [-1,9,-1],
                                       [-1,-1,-1]])
                    cam.color_image = cv2.filter2D(cam.color_image, -2, kernel)

                    #Run Filters to get masks
                    lock, unripe_bolls, ripe_bolls, mask1 = F.Harvest_Filter(cam.color_image)

                    #Mask to filter out bad data
                    depthMask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data
                    
                    #Generate the point cloud
                    pc = cam.FilteredCloud(mask1)

                    #Linear regression (usually where the errors are)
                    #Get the points in the x-z plane
                    X = np.transpose(pc[:,0]) #first column of the point cloud
                    Z = np.transpose(pc[:,2]) #third column of the point cloud
                    slope, y, r, p, se = stat.linregress(X, Z)
                    r = r**2
                except:
                    print("bad data")
                finally:
                        location.correct_theta(np.arctan(slope) - np.pi*(1-rowCounter%2), .75)#Adjust theta, add a correction factor for when on even rows
                        # location.correct_x() #Need to do some math to figure out how to correct this one.
                        break


            
            
            # Map
            totalbolls = ripe_bolls | unripe_bolls #bitwise or to combine the two measured bolls
            #Correct from index number to actual number:
            if(totalbolls == 2):
                totalbolls = 1
            elif(totalbolls == 3):
                totalbolls =2

            if(rowCounter%2 == 0):# we are only required to map even rows
                boll = 'P' + str(bollCounter)
                map.loc[rowCounter, boll] = totalbolls
            #Need to save the map to the flashdrive here
            print(map)
            # fine tune
                #Will need to move the robot by lock*correction factor
            LineUp() #Needs camera and pico - input is y distance MAKE SURE WE UPDATE THE OBSERVER!!!
            
            harvest(ripe)# see harvest filter function for value meanings
            # return done

            
            #Correct y location based on the boll
            if(rowCounter%2 == 0): #if on an even row we are measuring from the far wall to the boll
                m_y = -96 + 24 + boll_dist * bollCounter
            else: #if on an odd row we are measuring from the near wall to the boll
                m_y = -24 - boll_dist*bollCounter
            location.update_MY(m_y)
            
            #Correct x location based on a linear regression of the point cloud from the wall:
            # ## Generate point cloud
            # ### Generate and combine masks
            # depthMask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data
            # #### Combine the depth mask and the wall color mask
            # wall = wall/225 #Make the wall mask all 1s for next step
            # mask1 = np.logical_and(depthMask, wall) #And together so we get all of the points that are both good and the correct color
            # pc = cam.FilteredCloud(mask1)

            # ## Analyze the point cloud
            # #clear any data that is outside a box
            # pc = cv2.inrange(pc, [.004, .1], [-1,1]) #These values will need to be adjusted expiramentally.

            # #Get the points in the x-z plane
            # X = np.transpose(pc[:,0]) #first column of the point cloud
            # Z = np.transpose(pc[:,2]) #third column of the point cloud

            # slope, x, r, p, se = stat.linregress(X, Z)
            # theta = np.arctan(slope)

            # #update the observer:
            # location.update_MXT(x, theta)
            # #   status pin to return done
            # # reset status pin
            bulbCounter+=1
            WaitTillDone()
                #in function wait till pin is high
                # reset the pin
            location.time_old = time.time()
            state = 'wallfollow'

        case 'corner_in':
            ## RightCorner
            # turn corner
            # reset bol counter
            # return done
            #   status pin to return done
            # reset status pin
            # WallFollow
            turnLeft()
            bulbCounter = 0
            WaitTillDone()
            location.time_old = time.time()
            state = 'wallfollow'

        case 'corner_out':
            ## LeftCorner
            # turn corner
            # reset bol counter
            # return done
            #   status pin to return done
            # reset status pin
            # WallFollow
            turnRight()
            bulbCounter = 0
            WaitTillDone()
            location.time_old = time.time()
            state = 'wallfollow'

        case'end':
            ##end
            # maybe go back to start?
            # write map
            # idle
            ToCorner()
            # export CSV file in the prescribed format:
            manPD = pd.DataFrame(map)
            manPD.to_csv("map.csv", index_label="Row:")
            Idle()



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



location.correct_x(x_m, .5)
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
