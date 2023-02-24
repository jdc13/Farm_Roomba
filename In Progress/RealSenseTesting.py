#This code is designed to find various input parameters for the realsense camera
#Available test cases are: 
# frame: Cut out the edges of the frame that are not usable
# distance: Find the smallest distance to the wall measurable and standard deviations

# Tests will be run successively, starting with:
Test_Case = "calibration"


import numpy as np
import cv2
import RealSense as rs
import pandas as pd
import matplotlib.pyplot as plt

cam = rs.RSCam("Short")
ctx = rs.rs.context()
for d in ctx.devices:

    print ('Found device: ', \

            d.get_info(rs.rs.camera_info.name), ' ', \

            d.get_info(rs.rs.camera_info.serial_number))


SN = rs.rs.camera_info.serial_number


if Test_Case == "calibration":
    
    cam.get_frames()
    HSV = cv2.cvtColor(cam.color_image, cv2.COLOR_BGR2HSV)
    #Find the 3 colored dots
    wnd = "calibration"
    cv2.namedWindow(wnd)
    while(1):
        cam.get_frames()
        cv2.imshow(wnd, cam.usr_image())

        # im = cam.depth_image[]
        if cv2.waitKey(1) & 0xFF == ord('b'):
            break
    #Red
    HSVLow = np.array([37,171,0])
    HSVHigh = np.array([179,255,255])
    mask1 = cv2.inRange(HSV,HSVLow, HSVHigh)
    red = cam.FilteredCloud(mask1)
    # #Blue
    # HSVLow = np.array([33,113,88])
    # HSVHigh = np.array([113,255,182])
    # mask1 = cv2.inRange(HSV,HSVLow, HSVHigh)
    # print(np.sum(mask1))
    # blue = cam.FilteredCloud(mask1)
    # #purple
    # HSVLow = np.array([0,76,58])
    # HSVHigh = np.array([179,169,58])
    # mask1 = cv2.inRange(HSV,HSVLow, HSVHigh)
    # purple = cam.FilteredCloud(mask1)

    fig = plt.figure(1)
    ax = fig.add_subplot(projection = '3d')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    print(red)
    # print(blue)
    # print(purple)

    ax.scatter(red[:,0], red[:,1], red[:,2], color='r' )
    res = cv2.bitwise_and(cam.color_image,cam.color_image, mask =mask1)

    cv2.imshow(wnd, res)
    plt.show()

    
    # ax.scatter(blue[:,0], blue[:,1], blue[:,2] )
    # ax.scatter(purple[:,0], purple[:,1], purple[:,2] )
    plt.show()
    plt.waitforbuttonpress()
    while(1):
        pass





if Test_Case == "frame":
    print(Test_Case)
     #create the cv2 window to show trackbars
    wnd = "Crop The un-usable space around the sides"
    cv2.namedWindow(wnd)
    cam.get_frames() #update the image
    # print(np.shape(cam.depth_image))
    height = np.shape(cam.depth_image)[0]
    width = np.shape(cam.depth_image)[1]
    cv2.createTrackbar("Top", wnd,np.shape(cam.depth_image)[0],np.shape(cam.depth_image)[0],rs.nothing)
    cv2.createTrackbar("Bottom", wnd,0,np.shape(cam.depth_image)[0],rs.nothing)
    cv2.createTrackbar("Left", wnd,0,np.shape(cam.depth_image)[1],rs.nothing)
    cv2.createTrackbar("Right", wnd,np.shape(cam.depth_image)[1],np.shape(cam.depth_image)[1],rs.nothing)
    while(1):
        cam.get_frames()
        #Make a color map of the image so it is easier to see
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(cam.depth_image, alpha=0.03), cv2.COLORMAP_JET)
        #read trackbars
        top=cv2.getTrackbarPos("Top", wnd)
        bottom=cv2.getTrackbarPos("Bottom", wnd)
        left=cv2.getTrackbarPos("Left", wnd)
        right=cv2.getTrackbarPos("Right", wnd)
        #Crop image
        bnd = np.array([top,bottom,left,right])
        depth_colormap = rs.crop(depth_colormap,bnd)
        cv2.imshow(wnd, depth_colormap)

        # im = cam.depth_image[]
        if cv2.waitKey(1) & 0xFF == ord('b'):
            break

    crop = np.array([top,bottom,left,right])
    cv2.destroyAllWindows()
    Test_Case = "distance"

if Test_Case == "distance":
    wnd = "Distance\nGet the camera as close to a flat surface as possible\nthen press b"
    cv2.namedWindow(wnd)
    while(1):
        #Get the depth image, crop it then display it
        cam.get_frames()
        depth_image = rs.crop(cam.depth_image,crop)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        cv2.imshow(wnd, depth_colormap)

        if cv2.waitKey(1) & 0xFF == ord('b'):
            break
    # cv2.destroyAllWindows()

    mask1 = np.ones(np.shape(depth_image))
    mask1 = rs.crop(mask1,crop)

    cloud = cam.FilteredCloud(mask1)

    fig = plt.figure(1)
    ax = fig.add_subplot(projection = '3d')

    ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2] )
    plt.show()

    plt.figure(2)
    plt.scatter(cloud[:,1],cloud[:,2])
    plt.show()

    print('Press key to close')
    plt.waitforbuttonpress()
    plt.close()

# print(pc)
# depth_image = rs.zeroToNAN(depth_image)
# print(cam.depth_frame.get_data())
# print(cam.depth_image)
# print(depth_image)


#Store the 
        
