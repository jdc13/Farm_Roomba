import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
t = np.arange(-5,5,.2)
y = t*0 + (np.random.rand(np.size(t))*2 -1) + 3

plt.scatter(t,y)

slope, intercept, r, p, se = stat.linregress(t, y)
# print(slope, "\n", intercept,"\n",r**2)

theta = np.sin(slope)
d = intercept

plt.plot(t, t*slope + intercept)
thetadeg = theta*180/np.pi
print("theta: ", thetadeg)
print("d: ", d)

plt.show()