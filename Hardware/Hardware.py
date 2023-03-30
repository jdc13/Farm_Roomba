#This file will initialize any hardware that needs to be
#accessed from multiple locations.
import Hardware.RealSense as rs

cam = rs.RSCam(Range = "Short")