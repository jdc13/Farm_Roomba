# camera_tester.py
# This file contains code to take inputs from the realsense camera and generate meaurements to the wall


#Standard libraries
import csv
import cv2
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
#import time #time library for identifying the places where time is being lost, but its having bugs
import Filter as F

#custom libraries:
import RealSense as rs

#Initialize camera
cam = rs.RSCam(Range= "Short")

#Navigation parameters
target = .187325 #Desired distance from the wall, m - 0.2 puts robot base right at 8 inches, 0.187325 is 7.5 inches

cam.get_frames() #Reject 1st frame

# This try function is because the realsense camera was feeding bad data, to the point it was causing crashes. 
theta = 90
while(abs(theta) > 8):
    cam.get_frames() #update camera data
    # print("Have new frame")
    #Blur then sharpen the image to get a better filter result
    cam.color_image =  cv2.blur(cam.color_image,[10,10])
    kernel = np.array([[-1,-1,-1],
                        [-1,9,-1],
                        [-1,-1,-1]])
    cam.color_image = cv2.filter2D(cam.color_image, -2, kernel)
    
    # Will generate a mask that filters things out later.
    boll_loc, ripe_bolls, unripe_bolls = F.Harvest_Filter(cam.color_image)
    wall_mask = F.Wall_Filter(cam.color_image)
    wall_mask[0:40,:] = np.zeros([40,424])
    HSV = cv2.cvtColor(cam.color_image, cv2.COLOR_BGR2HSV)
    ripe_mask = cv2.inRange(HSV, F.ripe_low, F.ripe_high)
    ripe_mask = ripe_mask[:,42:383]
    unripe_mask = cv2.inRange(HSV,F.unripe_low, F.unripe_high)
    #combined_mask = cv2.add(ripe_mask, unripe_mask)
    # depthMask = cv2.inRange(cam.depth_image,0,1) #This mask filters out the bad data

    # Generate the point cloud:
    pc = cam.FilteredCloud(wall_mask)
    
    ### linear regression:

    # Analysis of the data started failing after implementing the filters. Set to keep trying to get a good frame until it works.
    #analyze the point cloud:
    #Get the points in the x-z plane
    X = np.transpose(pc[:,0]) #first column of the point cloud
    Z = np.transpose(pc[:,2]) #third column of the point cloud

    #T=np.stack((X,Z))
    

    #data = [X,Z]
    #with open('tmp_file.txt', 'w') as f:
    #    csv.writer(f, delimiter=' ').writerows(data)
    length = np.arange(-.3,.4,.1)
    
    slope, intercept, r, p, se = stat.linregress(X, Z)
    r2 = r**2
    # print("R Squared: ", r2)


    '''
    wall = slope*length + intercept
    residual =np.absolute(np.subtract(wall,Z))
    for i in range(10):
        max_residual_index = residual.index(max(residual))
        residual = residual[:max_residual_index] + residual[max_residual_index + 1:]
        X = X[:max_residual_index] + X[max_residual_index + 1:]
        Z = Z[:max_residual_index] + Z[max_residual_index + 1:]
    
    
    slope, intercept, r, p, se = stat.linregress(X, Z)
    
    '''
    # throw away points in array with highest residuals, save new array of points
    # redo regression


    # print(slope)
    #Find the angle and run the controller.
    x = intercept * 39.3700787
    theta = np.degrees(np.arctan(slope))
    print("Theta: ", theta)

print("x: ", x)
print(boll_loc, "\t", ripe_bolls, "\t", unripe_bolls)
cv2.imshow("Blurred image and depth image", cam.usr_image())
cv2.imshow("wall_mask", wall_mask)
cv2.imshow("ripe_mask", ripe_mask)
cv2.imshow("unripe_mask", unripe_mask)
#cv2.imshow("combined_mask", combined_mask)

#Visualization code:
fig = plt.figure(1)
length = np.arange(-.3,.4,.1)
wall = slope*length + intercept
#residual = wall - Z
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
