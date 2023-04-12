#This file will be the base file that calls all other functions. 
# from Hardware import Hardware as dev
import numpy as np
import pandas as pd



#States:
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
    loc_phys = np.zeros((1,2), float) #X and Y coordinates
    loc_map = np.zeros((1,2), int) # row and plant location

#initialize a dataframe of 0s the size of the map
#6 rows, 9 plants
map = pd.DataFrame(np.zeros((6,9)), 
                   index=[1,2,3,4,5,6], 
                   columns=['P1','P2','P3','P4','P5','P6','P7','P8','P9'])

# add switch statement

## init
# set up
# wallfollow

## wallfollow
#
# sample


## Harvest
# stop at bol
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