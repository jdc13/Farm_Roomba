import numpy as np
import cv2
from scipy import ndimage


# HSV Filter codes: Tune as necessary
wall_high = np.array([70, 255, 120]) # Some areas of the wall are masked, but there is enough visible to get a good reading.
wall_low = np.array([0, 0, 0])

ripe_high = np.array([179, 114, 255]) #The values are really tight, because the glare on the dowells makes them pretty white.
ripe_low = np.array([32, 0, 200])

unripe_high = np.array([118, 255, 255]) #This one is super easy for the filter to see.
unripe_low = np.array([57, 101, 0])

# distance measurement conversion
pixels_per_inch = 77.1 # Image is 424 pixels across. At 7.5 in from wall, camera sees approx. 10 inches of wall and *5.5* inches at level of bolls. 424/5.5 = 77.1
pixels_center = 212


def find_bolls(mask, tolerance):
    '''
    This function takes in a mask and determines whether or not there are bolls in it
    Tolerance is used as a threshold value for the color matching
    '''
    #Divide the mask in 2
    # print(mask)
    [top, bottom] = np.vsplit(mask,2)
    
    bolls = 11 #Starting value
    # print(np.sum(bottom))
    if(np.sum(bottom) > tolerance):
        bolls -= 1
    if(np.sum(top) > tolerance):
        bolls -=10
    
    return bolls

def Harvest_Filter(color_image):
    '''
    This function returns:
    The horizontal position of the bolls "boll_loc" for correction
    The number and position of the bolls. 
    Represented as binary numbers. 1 = bottom, 10 = top. 
    Can return 0, 1, 2, 3 representing none, bottom only , top only, both respectively.
    a raw mask for the location of the wall
    '''

    HSV = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        # src	input image: 8-bit unsigned, 16-bit unsigned ( CV_16UC... ), or single-precision floating-point.
        # dst	output image of the same size and depth as src.
        
    ripe_mask = cv2.inRange(HSV, ripe_low, ripe_high)
    unripe_mask = cv2.inRange(HSV,unripe_low, unripe_high)
        # src	first input array.
        # lowerb	inclusive lower boundary array or a scalar.
        # upperb	inclusive upper boundary array or a scalar.
        # returns
        # dst	output array of the same size as src and CV_8U type.
    
    combined_mask = cv2.add(ripe_mask, unripe_mask) #Combine the two masks to look at the ripe and unripe bolls at the same time

    #finds boll location in next 2 lines
    ripe_bolls = find_bolls(ripe_mask, 50) #This tolerance needs to be found expirimentally 
    unripe_bolls = find_bolls(unripe_mask, 50) #Tolerance needs to be found exipirimentally

    # Find the location of the ripe bolls
    # combined_mask = np.logical_or(ripe_mask, unripe_mask) #Combine the two masks to look at the ripe and unripe bolls at the same time
    boll_loc, _ = ndimage.center_of_mass(ripe_mask) # finds pixel location of the center of the boll x(boll_loc) i 0 to ~300(left to right);

    boll_loc = (boll_loc - pixels_center) / pixels_per_inch # in inches: negative if boll is on left side, positive for right
    return boll_loc, ripe_bolls, unripe_bolls

def Wall_Filter(color_image):
    HSV = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
    wall_mask = cv2.inRange(HSV, wall_low, wall_high)
    return wall_mask
    



