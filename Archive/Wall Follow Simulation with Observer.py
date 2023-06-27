import controlers as ctr
import numpy as np
import matplotlib.pyplot as plt
import wallFollow_class as WFClass
#potential sources of error:                Model with:
#Sensor noise                               Add random noise to sensor
#inaccurate time                            Add random noise to observer time
#speeds not synced for short periods        Update observer and physical system at separate times
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


#observer:
location = WFClass.position_observer()
tObsUpdate = .05  #Time between updating positions on the observer

#Simulation Parameters
Tstep = 0.001
tsim = np.arange(0,8,Tstep) #Duration and step size for simulation

#initial Y values:
top = 3
y0 = np.arange(0,3*top/2,top/2) #Look at initial points that start at several locations on either side of the target line

x = np.zeros([np.size(tsim), np.size(y0)])
y = np.zeros([np.size(tsim), np.size(y0)])
y[0]=y0
Theta = np.zeros([np.size(tsim), np.size(y0)])
vtime = np.zeros([np.size(tsim), np.size(y0)])
dtime = np.zeros([np.size(tsim), np.size(y0)])
#Values to track observer
obs_xtime = np.zeros([np.size(tsim), np.size(y0)])
obs_ytime = np.zeros([np.size(tsim), np.size(y0)])
obs_thetatime = np.zeros([np.size(tsim), np.size(y0)])

#Real-time plots:


for j in range(0,np.size(y0)):
    # print(j)

    fig = plt.figure(1)
    plt.ion()
    pathPlot = plt.subplot(2,1,1)
    plt.title("Path")
    thetaplot = plt.subplot(2,1,2)
    plt.title("Angle")
    plt.show()

    WF = WFClass.WallFollow(sim=True)
    
    #Initial Conditions
    location.state = np.array([[0],
                               [y[0,j]],
                               [0]])
    # print(location.state)
    
    skips = 40 #number of time intervals to skip between updating the controller
    update = 5 #number of time intervals to skip between updating the observer
    #Run Simulation
    flag = True
    for i in range(0,np.size(tsim)-1):
        
        xobs = location.state[0]
        yobs =location.state.item(1)
        thetaobs = location.state[2]

        # v, dtheta, r = WF.update_sim(thetaobs, y[i,j], Tstep)
        # print(yobs - y[i,j])
        if(i % skips == 0):
            
            # v,dtheta, r = WF.update_sim(Theta[i,j], yobs, Tstep*(skips+1))
            # v, dtheta, r = WF.update_sim(thetaobs, y[i,j], Tstep*skips)
            v, dtheta = WF.update_sim(thetaobs, yobs, Tstep*skips)
            location.update_DR(v, dtheta, Tstep*skips)
        if(xobs % update < .25 and flag):
            flag = False
            location.correct_x(x[i,j] + .25*(1-2*np.random.rand()), .5)
            location.correct_y(y[i,j] + .05*(1-2*np.random.rand()), .5)
            location.correct_theta(Theta[i,j] + .005*(1-2*np.random.rand()), .75)
            # location.state[1] += .5*( y[i,j] + .05*(1-2*np.random.rand())-location.state[1])
            # location.state[0] += .5*( x[i,j] + .25*(1-2*np.random.rand())- location.state[0])
            # #More error expected in X update since there will be spacing error.
            # location.state[2] += .75*(Theta[i,j] + .005*(1-2*np.random.rand())- location.state[2])
        if(xobs % update > .5):
            flag = True
        obs_xtime[i+1][j] = location.state[0]
        obs_ytime[i+1][j] = location.state[1]
        obs_thetatime[i+1][j]=location.state[2]

        
        dy = v*np.sin(Theta[i][j])*Tstep
        dx = v*np.cos(Theta[i][j])*Tstep
        # print(dy, "\t", dx, "\t", dtheta)
        x[i+1][j] =x[i][j]+dx
        y[i+1][j] =y[i][j]+dy
        Theta[i+1][j] =Theta[i][j] + dtheta*Tstep#= ctr.saturate(Theta[i][j]+dtheta,ThetaMin,ThetaMax)

        if(i % 100 == 1):
            pathPlot.cla()
            thetaplot.cla()
            pathPlot.plot(x[0:i,j], y[0:i,j])
            pathPlot.plot(obs_xtime[1:i,j], obs_ytime[1:i,j])
            thetaplot.plot(tsim[0:i], Theta[0:i,j])
            thetaplot.plot(tsim[0:i], obs_thetatime[0:i,j])

            plt.show()
            plt.pause(0.01)

        #show simulation:
    plt.waitforbuttonpress()
    pathPlot.cla()
    thetaplot.cla()

        
            

        
        
    

# #Figure 1:
# plt.figure(1)
# ax = plt.subplot(2,2,1)
# ax.title.set_text("Path")
# ax.set_xlim(-1,30)
# for i in range(0,np.size(y0)):
#     plt.plot(x[:,i],y[:,i])

# ax = plt.subplot(2,2,2)
# ax.title.set_text("estimated path")
# for i in range(0,np.size(y0)):
#     plt.plot(vtime[:,i],dtime[:,i])


# ax = plt.subplot(2,2,3)
# ax.title.set_text("estimated theta")
# for i in range(0,np.size(y0)):
#     plt.plot(tsim[:],dtime[:,i])

# ax = plt.subplot(2,2,4)
# ax.title.set_text("Theta over Time")
# ax.set_ylim(ThetaMin*180/np.pi,ThetaMax*180/np.pi)
# for i in range(0,np.size(y0)):
#     plt.plot(tsim[:],Theta[:,i]*180/np.pi)

# plt.figure(2)
# for i in range(0,np.size(y0)):
#     plt.plot(tsim[:],dtime[:,i])





# plt.show()