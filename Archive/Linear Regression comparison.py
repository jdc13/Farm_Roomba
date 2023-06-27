#This script is to test different linear regression methods to see what is faster. It won't be used in the robot.
#Findings: the scipy method is about twice as fast I did some research and found that it was generally accepted as the fastest method.
#this was the method used in the original program
#Created by Josh Chapman

import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.stats as stat

size = 100000
x = np.arange(0,size,.1)#Create a massive array
y = 10 * x + 2 + np.random.normal(0, 100000, np.size(x))

# plt.scatter(x,y)

told = time.time()
A = np.ones([np.size(x),2])
A[:,1] = x
# print(A.T@A)
a = np.linalg.inv(A.T@A)@A.T@y
# print(a)
y1 = a.item(0)
slope = a.item(1)
ybar = np.mean(y)
yhat = a.item(0) + a.item(1) * x


st = np.sum((y-ybar)**2)
sr = np.sum((y-yhat)**2)
r2 = (st-sr)/st
# print(st)
# print(sr)

tel = time.time()-told
print("Elapsed time: ", tel)
print(r2)



# plt.scatter(x, yhat)
# # plt.show()
# plt.waitforbuttonpress()


#Second method

told = time.time()


slope, y, r, p, se = stat.linregress(x, y)
r = r**2
tel = time.time() - told

print("\n\n Second Method:\n Elapsed time: ", tel)
