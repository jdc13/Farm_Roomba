import numpy as np
import cv2
from scipy import ndimage
# HSV Filter codes
wall_high = np.array([225, 225, 225])
wall_low = np.array([0,0,0])

ripe_high = np.array([225,225,225])
ripe_low = np.array([0,0,0])

unripe_high = np.array([225,225,225])
unripe_low = np.array([0,0,0])


def find_bolls(mask, tolerance):
    '''
    This function takes in a mask and determines whether or not there are bolls in it
    Tolerance is used as a threshold value for the color matching
    '''
    #Divide the mask in 2
    top, bottom = np.vsplit(mask,2)
    
    bolls = 0 #Starting value
    if(sum(bottom) > tolerance):
        bolls += 1
    if(sum(top) > tolerance):
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
    ripe_mask = cv2.inrange(HSV, ripe_low,ripe_high)
    wall_mask = cv2.inrange(HSV, wall_low,wall_high)
    unripe_mask = cv2.inrange(HSV,unripe_low,unripe_high)

    ripe_bolls = find_bolls(ripe_mask, 100) #This tolerance needs to be found expirimentally
    unripe_bolls = find_bolls(unripe_mask, 100) #Tolerance needs to be found exipirimentally

    # Find the location of the bolls
    combined_mask = np.logical_or(ripe_mask, unripe_mask) #Combine the two masks to look at the ripe and unripe bolls at the same time
    lock, y = ndimage.center_of_mass(combined_mask)

    return lock, unripe_bolls, ripe_bolls, wall_mask
    



