import controlers as ctr
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt

Target = 0 #Distance from the wall
#Physical Parameters of the system:
L = 12 #Distance between wheels

#Controller Parameters:
t = .5  #Desired Rise Time of the system
z = .707
vmax = 5 #in/s
vmin = 0 #in/s
Dmax = 2*vmax #difference in speed between the two wheels
Dmin = -1*Dmax
sigma = .01
ThetaMax = np.pi/3 #Just shy of 90 degrees
ThetaMin = -1*ThetaMax#just shy of 90 degrees

#Transfer Function Variables
b0 = vmax/L
a0 = a1 = 0

#Simulation Parameters
Tstep = 0.0001
tsim = np.arange(0,8,Tstep) #Duration and step size for simulation

#initial Y values:
top = 3
y0 = np.arange(top/2,3*top/2,top/2) #Look at initial points that start at several locations on either side of the target line

x = np.zeros([np.size(tsim), np.size(y0)])
y = np.zeros([np.size(tsim), np.size(y0)])
y[0]=y0
Theta = np.zeros([np.size(tsim), np.size(y0)])
vtime = np.zeros([np.size(tsim), np.size(y0)])
dtime = np.zeros([np.size(tsim), np.size(y0)])
for j in range(0,np.size(y0)):
    # print(j)

    LF = ctr.PD2ndOrderADV(b0, a1, a0, t, z, sigma, Tstep, Dmin, Dmax) #Line Following Controller
    # LF.showParams()
    
    #Initial Conditions
    
    
    #Run Simulation
    for i in range(0,np.size(tsim)-1):
        p = y[i][j]
        # print(p)
        d = LF.update(Target, p)
        if abs(Theta[i,j]) > ThetaMax*4/5:
            v = vmax
        else:
            v = vmax - (vmax-vmin)*(abs(d)/Dmax)#**(1/2)
        dy = v*np.sin(Theta[i][j])*Tstep
        dx = v*np.cos(Theta[i][j])*Tstep
        dtheta = d/L *Tstep
        x[i+1][j] =x[i][j]+dx
        y[i+1][j] =y[i][j]+dy
        Theta[i+1][j] = ctr.saturate(Theta[i][j]+dtheta,ThetaMin,ThetaMax)
        vtime[i+1][j]=v
        dtime[i+1][j]=d
    

#Figure 1:
plt.figure(1)
ax = plt.subplot(2,2,1)
ax.title.set_text("Path")
ax.set_xlim(0,10)
for i in range(0,np.size(y0)):
    plt.plot(x[:,i],y[:,i])

ax = plt.subplot(2,2,2)
ax.title.set_text("v over Time")
for i in range(0,np.size(y0)):
    plt.plot(tsim[:],vtime[:,i])


ax = plt.subplot(2,2,3)
ax.title.set_text("D over Time")
for i in range(0,np.size(y0)):
    plt.plot(tsim[:],dtime[:,i])

ax = plt.subplot(2,2,4)
ax.title.set_text("Theta over Time")
ax.set_ylim(ThetaMin*180/np.pi,ThetaMax*180/np.pi)
for i in range(0,np.size(y0)):
    plt.plot(tsim[:],Theta[:,i]*180/np.pi)

# plt.figure(2)
# for i in range(0,np.size(y0)):
#     plt.plot(tsim[:],dtime[:,i])





plt.show()