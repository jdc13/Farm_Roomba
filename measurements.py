# measurements.py
# This file contains code to take inputs from the realsense camera and generate a location relative to the wall and bolls

#Standard libraries
import cv2
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
import time #time library for identifying the places where time is being lost
import Filter as F
import RealSense as RS

cam = RS.RSCam(Range= "Short")
cam.get_frames() #Reject first frame (it's really dark.)

#  Initialize variables that we will need later.
def measure_x_theta():

    # This try function is because the realsense camera was feeding bad data, to the point it was causing crashes.
    # We should still be able to read the locations of the bolls from the camera.  
    try:  
        theta = 90
        while(abs(theta) > 8):
            ### Get the Image               
            cam.get_frames()#update camera data
            cam.color_image =  cv2.blur(cam.color_image,[10,10])  #Blur then sharpen the image to get a better filter result
            kernel = np.array([[-1,-1,-1],
                                [-1,9,-1],
                                [-1,-1,-1]])
            cam.color_image = cv2.filter2D(cam.color_image, -2, kernel)
            
            ### Filter Image
            wall_mask = F.Wall_Filter(cam.color_image)
            wall_mask[0:40,:] = np.zeros([40,424])
            depth_mask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data

            ### Generate the point cloud:
            pc = cam.FilteredCloud(wall_mask) # and depth_mask?

            ### Linear Regression:
            # Analysis of the data started failing after implementing the filters...
            #analyze the point cloud:
            #Get the points in the x-z plane
            X = np.transpose(pc[:,0]) #first column of the point cloud
            Z = np.transpose(pc[:,2]) #third column of the point cloud
            slope, intercept, r, p, se = stat.linregress(X, Z) 
            x = intercept * 39.3700787 # converting meters to inches
            theta = np.degrees(np.arctan(slope))
            # r2 = r**2
            
        print("x_meas: ", x)
        print("theta_meas: ", theta)
        return x, theta
    except:
        print("bad data")

def measure_y():
    cam.get_frames() # update camera data
    cam.color_image =  cv2.blur(cam.color_image,[10,10])  #Blur then sharpen the image to get a better filter result
    kernel = np.array([[-1,-1,-1],
                        [-1,9,-1],
                        [-1,-1,-1]])
    cam.color_image = cv2.filter2D(cam.color_image, -2, kernel)
    y_meas, _, _ = F.Harvest_Filter(cam.color_image)
    return y_meas

def measure_ripe():
    cam.get_frames()#update camera data
    #print("Have new frame")
    cam.color_image =  cv2.blur(cam.color_image,[10,10])  #Blur then sharpen the image to get a better filter result
    kernel = np.array([[-1,-1,-1],
                        [-1,9,-1],
                        [-1,-1,-1]])
    cam.color_image = cv2.filter2D(cam.color_image, -2, kernel)
    _, ripe_bolls, unripe_bolls = F.Harvest_Filter(cam.color_image)




'''
#Visualization code:
print(boll_loc, "\t", ripe_bolls, "\t", unripe_bolls)
cv2.imshow("Blurred image and depth image", cam.usr_image())
cv2.imshow("wall_mask", wall_mask)
cv2.imshow("ripe_mask", ripe_mask)
cv2.imshow("unripe_mask", unripe_mask)
cv2.imshow("combined_mask", combined_mask)

fig = plt.figure(1)
length = np.arange(-.3,.4,.1)
wall = slope*length + intercept
tar = np.ones(np.shape(length))*target

plt.title("looking down")
plt.xlim([-.3,.3])
plt.ylim([0, .6])
plt.scatter(X,Z)
plt.plot(length, wall)
plt.plot(length, tar)
plt.draw()
plt.show()
plt.pause(0.01)
plt.cla() 
'''
