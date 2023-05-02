#Realsense.py
#Created by: Josh Chapman       Date: 1/12/2023
#This code contains basic implementation for the Realsense camera
#Version 1.0
#Status: Complete
#Capabilities:
    # Camera initialization
    # Getting frames and storing as np arrays
    # ouput of a user-readable image
    # Align depth with color image
    # Select long, medium or short ranges
    # Return a 3D space vector when given a point
    # Generate a point cloud based on a mask like what you would get on numpy.
        #Number of points is limited to ~100
#Abandoned:
    # Calibrate depth image (possibly store to a csv or json file)
        #Skipping this. The camera appears to be well calibrated to start. We can revise this if needed.


#potential fixes:
    #Potentially take only some depth frames to reduce processing load 
    #errosion and dialation (remove large noise)
    #Yolo-v7 for AI object detection

#Developed by combining and editing code from:
#https://github.com/IntelRealSense/librealsense/tree/development/wrappers/python/examples
#Techniques for editing detection ranges:
#https://dev.intelrealsense.com/docs/tuning-depth-cameras-for-best-performance
    #This doesn't have any code implementaiton, so will need to find equivalent tools in python library.
    #This page also includes information on error


#Non-Standard Dependencies:
    #Dependency     install command             import line
    #Pyrealsense2   pip install pyrealsense2    import pyrealsense2
    #OpenCV         pip install opencv-python   import cv2     

#To get it working on raspbery pi, see:
    # https://dev.intelrealsense.com/docs/using-depth-camera-with-raspberry-pi-3
    # https://www.reddit.com/r/realsense/comments/hn0hfe/anyone_about_to_install_pyrealsense2_on_raspbian/
    
#Compatibility fix for raspberry pi
try:
    #This block will run on a PC
    import pyrealsense2 as rs
    rs.pipeline() #Call a random RS case to see if the library is imported properly
    pclim = 100 # The maximum number of points that the point cloud will return.
except:
    #The above block will error on a RPi, so we can assume that these variables will be used.
    import pyrealsense2.pyrealsense2 as rs
    pclim = 50 #The maxiumum number of points that the point cloud will return



import cv2
import numpy as np
import time
# from io import StringIO as st
# import pandas as pd


class RSCam:
    '''
    A class for implementing the Intel RealSense D415. 

    '''
    
    def __init__(self,Range = "Long"): #Lower range = lower resolution
        '''
        Lower range = lower resolution. Options are:
        "Long", "Mid", "Short"
        Default is "Long"
        '''
        #Set up RS objects
        self.pc = rs.pointcloud()
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        
        # Set the detection range of the camera
        if Range == "Long":
            camX = 1280
            camY = 720
        elif Range == "Mid":
            camX = 640
            camY = 480
        elif Range == "Short":
            camX = 424
            camY = 240

        # Enable the camera
        self.config.enable_stream(rs.stream.depth, camX, camY, rs.format.z16, 30) 
        self.config.enable_stream(rs.stream.color, camX, camY, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

    def get_frames(self): 
        '''
        Retrieve and align data from the camera.
        Data is stored as RS frames and as numpy arrays for different processing tasks. 
        The numpy arrays are returned by this function.
        '''
        while True:
        # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()
            
            #align frames
            self.frames = self.align.process(frames)
            self.depth_frame = frames.get_depth_frame()
            self.color_frame = frames.get_color_frame()
            if not self.depth_frame or not self.color_frame:
                continue
            else:
                break
        
        # Convert images to numpy arrays for OpenCV processing
        self.depth_image = np.asanyarray(self.depth_frame.get_data())
        self.color_image = np.asanyarray(self.color_frame.get_data())
        
        
        return [self.color_image, self.depth_image]

    def usr_image(self):
        '''
        Create and return a side by side image of the color image and depth map
        '''
        
        # Change the depth image to a color map to make it easier to see
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(self.depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        # If depth and color resolutions are different, resize color image to match depth image for display
        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = self.color_image.shape
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(self.color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            return np.hstack((resized_color_image, depth_colormap)) #Combine Images
        else:
            return np.hstack((self.color_image,depth_colormap)) #Combine Images
          
    def deproject_Point(self, x = np.zeros(2)): 
        '''
        Given a 2D point in the image space, find the 3D point in real space
        # Note: This is a processor intense process. It is better to use FilteredCloud() for multiple points
        '''

        depth_intrin = self.depth_frame.profile.as_video_stream_profile().intrinsics
        depth = self.depth_frame.get_distance(x[0],x[1])
        return rs.rs2_deproject_pixel_to_point(depth_intrin, x, depth)

    def FilteredCloud(self, mask): 
        '''
        Return a point cloud of no more than a set number of points specific to the hardware
        being used. The points will corespond to unmasked locations in the input mask.
        '''

        depth = self.depth_frame
        #Generate the point cloud
        self.pc.map_to(self.color_frame) 
        points = self.pc.calculate(depth)

        # #Possibly faster method:
        # v, t = points.get_vertices(), points.get_texture_coordinates()
        # verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
        # texcoords = np.asanyarray(t).view(np.float32).reshape(-1, 2)  # uv


        # Bad points appear as 0,0,0 in the point cloud, and correspond to 0 in the depth image.
        # Extracting points is a processor heavy process, because of the way RealSense stores the cloud.
        # Because RealSense isn't officially supported, don't expect this to be fixed.
        # To limit the number of bad points we waste time processing, we will create a mask based on 
        # the depth image.
        
        depthMask = cv2.inRange(self.depth_image,0,1) #This mask finds the bad data points

        #Combine the depth mask with the input mask.
        #Change the arrays to booleans for logical operations
        depthMask = depthMask.astype(bool)
        mask = mask.astype(bool) 
        # We want to overlap the good data points with the input mask
        # Since the depth mask is the locations of the bad data points, we just not it 
        mask = np.logical_and(mask,np.logical_not(depthMask))
        
        #Prepare the mask for processing
        mask = mask.flatten() #Make the mask and the point cloud the same dimension
        loc = np.nonzero(mask)#Get the indecies of the non-0 elements of the mask
        
        #Find the number of points to skip to get an evenly spaced cloud within the allowed number of points
        if np.size(loc) > pclim:         
            n = int(np.size(loc)/pclim)
        else:
            n = 1

        #Extract the 3D coordinates
        vtx = np.asarray(points.get_vertices()) 
        
        objectCloud = []#initialize empty list
        i = 0 #Initialize the index to 0
        
        while i < np.size(loc):
            #data type handling:
            line = str(vtx[loc[0][i]])#Convert to a string so we know what the datatype is
            # remove the parenthases from the string
            line = line[1:]
            line = line[:-1]
            
            temp = line.split(",") #divide the numbers into a list
            #convert the strings to float
            temp = map(float, temp)
            cord = list(temp)
            
            if sum(cord) != 0: #Check to make sure a bad point didn't slip through
                objectCloud.append(cord) #Good data point, add it and move to the next
                i += n #Skip n coordinates
            else:
                i +=1 #Bad data point, reject it.

        return  np.array(objectCloud)
        

         



#Use area below as example code:
# def nothing(blank):
#     pass

# import matplotlib.pyplot as plt
    

# cam = RSCam(Range = "Short")
# cv2.namedWindow('RealSense',cv2.WINDOW_AUTOSIZE)
 
# #assign strings for ease of coding
# hh='Hue High'
# hl='Hue Low'
# sh='Saturation High'
# sl='Saturation Low'
# vh='Value High'
# vl='Value Low'
# wnd = 'Filter Bars'
# cv2.namedWindow(wnd) #Create a window named 'Colorbars'
# #Begin Creating trackbars for each
# cv2.createTrackbar(hl, wnd,0,179,nothing)
# cv2.createTrackbar(hh, wnd,179,179,nothing)
# cv2.createTrackbar(sl, wnd,99,255,nothing)
# cv2.createTrackbar(sh, wnd,255,255,nothing)
# cv2.createTrackbar(vl, wnd,89,255,nothing)
# cv2.createTrackbar(vh, wnd,240,255,nothing)

# #point cloud visualization
# fig = plt.figure(1)
# ax = fig.add_subplot(projection = '3d')

# while(1):
#     cam.get_frames()
#     cv2.imshow('RealSense', cam.usr_image())
#     # print(cam.deproject_Point(np.array([100,100])))

#     #Convert frames to HSV
#     HSV = cv2.cvtColor(cam.color_image, cv2.COLOR_BGR2HSV)

#     #Read trackbars
#     hul=cv2.getTrackbarPos(hl, wnd)
#     huh=cv2.getTrackbarPos(hh, wnd)
#     sal=cv2.getTrackbarPos(sl, wnd)
#     sah=cv2.getTrackbarPos(sh, wnd)
#     val=cv2.getTrackbarPos(vl, wnd)
#     vah=cv2.getTrackbarPos(vh, wnd)
 
#     #make array for final values
#     HSVLOW=np.array([hul,sal,val])
#     HSVHIGH=np.array([huh,sah,vah])

#     mask1 = cv2.inRange(HSV,HSVLOW, HSVHIGH)
#     #Create a filtered image
#     res = cv2.bitwise_and(cam.color_image,cam.color_image, mask =mask1)

#     cv2.imshow(wnd, res)

#     if cv2.waitKey(1) & 0xFF == ord('b'):
#         break

# while(1):
#     cam.get_frames()
#     HSV = cv2.cvtColor(cam.color_image, cv2.COLOR_BGR2HSV)
#     mask1 = cv2.inRange(HSV,HSVLOW, HSVHIGH)
#     cloud = cam.FilteredCloud(mask1)
#     cv2.imshow('RealSense', cam.usr_image())
   
    
#     # plt.scatter(cloud[:][0], cloud[:][1], cloud[:][2])

#     # a = cloud
    
#     # print(type(cloud[0][0]))
#     if np.size(cloud) > 6:
#         print(np.shape(cloud), "\t", cloud[0:5][1])
#         ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2] )
#         plt.show()
#         cv2.imshow('RealSense', cam.usr_image())
#         break
       
     

# while(1):
#     if cv2.waitKey(1) & 0xFF == ord('b'):
#         break
    








