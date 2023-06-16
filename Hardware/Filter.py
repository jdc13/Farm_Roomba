import numpy as np
import cv2
from scipy import ndimage

# HSV Filter codes
wall_high = np.array([225, 225, 225]) #([70, 255, 120]) # Some areas of the wall are masked, but there is enough visible to get a good reading.
wall_low = np.array([0, 0, 0])

ripe_high = np.array([179, 114, 255]) #The values are really tight, because the glare on the dowells makes them pretty white.
ripe_low = np.array([32, 0, 200])

unripe_high = np.array([118, 255, 255]) #This one is super easy for the filter to see.
unripe_low = np.array([57, 101, 0])


def find_bolls(mask, tolerance):
    '''
    This function takes in a mask and determines whether or not there are bolls in it
    Tolerance is used as a threshold value for the color matching
    '''
    #Divide the mask in 2
    print(mask)
    [top, bottom] = np.vsplit(mask,2)
    
    bolls = 0 #Starting value
    # print(np.sum(bottom))
    if(np.sum(bottom) > tolerance):
        bolls += 1
    if(np.sum(top) > tolerance):
        bolls +=10
    
    return bolls




def Harvest_Filter(color_image):
    '''
    This function returns:
    The horizontal position of the bolls "lock" for correction
    The number and position of the bolls. 
    Represented as binary numbers. 1 = bottom, 10 = top. 
    Can return 0, 1, 2, 3 representing none, bottom only , top only, both respectively.
    a raw mask for the location of the wall
    '''

    HSV = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
    ripe_mask = cv2.inRange(HSV, ripe_low,ripe_high)
    wall_mask = cv2.inRange(HSV, wall_low,wall_high)
    unripe_mask = cv2.inRange(HSV,unripe_low,unripe_high)

    ripe_bolls = find_bolls(ripe_mask, 100) #This tolerance needs to be found expirimentally
    unripe_bolls = find_bolls(unripe_mask, 100) #Tolerance needs to be found exipirimentally

    # Find the location of the ripe bolls
    # combined_mask = np.logical_or(ripe_mask, unripe_mask) #Combine the two masks to look at the ripe and unripe bolls at the same time
    lock, y = ndimage.center_of_mass(ripe_mask)

    return lock, unripe_bolls, ripe_bolls, wall_mask
    



