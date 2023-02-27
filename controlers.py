#controlers.py
#This file contains several controllers to be used in different types of systems. The controlers are developed based on
#the BYU controls class, and are intended to allow for quick design of control loops based on the transfer function of the system.
#This file is currently under development. changes to controllers may be made and cause problems. Some blocks of code may be rather messy.
#Created by Josh Chapman

import mpmath as np

live = False #Set time step to this to use actual elapsed time in the integrals and derivatives.
import time

class PD2ndOrder:#PD controller using pure derivative
    #Physical System Transfer Function:
    #       b0
    # s**2 + a1*s + a0
    
    #Desired Reponse Parameters:
    # wn = Natural Frequency
    # z = Damping Ratio
    
    
    def __init__(self, 
                 b0, a1, a0, #Physical System Transfer Function
                 tr, z, #Desired rise time and damping ratio
                 Tstep, #Time step for descrete
                 mn=0, mx=0 #Saturation limits for the output
                 ): 
                
        #operating variables
        self.timeOld = 0            #Variable to store old time for live calculations
        self.firstRun = True        #Tells whether or not the controller is on its first run
        self.Tstep = Tstep          #time step for simulation
        self.yold = 0               #Old value for differentiator and integrators

        #Physical system transfer coefficients
        self.a1 = a1                
        self.a0 = a0
        self.b0 = b0
        
        #output saturation limits
        self.mn = mn
        self.mx = mx
        
        #Desired closed loop characteristics
        self.wn = 2.2/tr
        self.z = z
        
        #Find controller parameters:
        self.kd = (2*z*self.wn-a1)/b0
        self.kp = (self.wn**2-a0)/b0
        
        #Find DC gain of the sysetem:
        self.k = b0*self.kp/self.wn**2
        
        
        

    def update(self, ref, y):
        #Numerical Derivative
        now = 0
        if self.Tstep == live:
            now = time.time()

        #only do derivative if there is a previous value to refference
        if self.firstRun: 
            self.firstRun = False
            d = 0
        else:
            if self.Tstep == live:
                d = (y-self.yold)/(now-self.timeOld) #Calculate derivative based on 
                self.timeOld = now #Update time
            else:
                d = (y-self.yold)/self.Tstep 
        
        #save current point as the old point for next iteration
        self.yold = y

        #calculate output and return it      
        u = (ref-y)*self.kp - d*self.kd   #Multipy the error by kp, subtract kd*dy
        return(saturate(u, self.mn, self.mx))

    def showParams(self):
        print("Parameters:",
              "\nkd =\t", self.kd,
              "\nkp =\t", self.kp,
              "\nk =\t",  self.k)
    
    def showCharEquation(self):
        print("Characteristic Equation:",
               "\ns**2 + ", self.a1+self.b0*self.kd,"*s + ", self.a0 + self.b0*self.kp,
               "\ns**2 + ", 2*self.wn*self.z,"*s + ", self.wn**2,
               "\nThe equations are calculated differently, but should be equivalent."  )
        
        
    def showPoles(self):  
        alph1 = 2*self.wn*self.z
        alph0 = self.wn**2
        print("Poles:\n",
              (-1*alph1 + np.sqrt(alph1**2-4*alph0))/2, "\n",
              (-1*alph1 - np.sqrt(alph1**2-4*alph0))/2)

class PD2ndOrderADV:#PD controller using dirty derivative (pure derivative combined with a low pass filter)
    #Physical System Transfer Function:
    #       b0
    # s**2 + a1*s + a0
    
    #Desired Reponse Parameters:
    # wn = Natural Frequency
    # z = Damping Ratio
    
    
    def __init__(self, 
                 b0, a1, a0,    #Physical System Transfer Function
                 tr, z, sigma,  #Controled system parameters, inverse of cutoff frequency for low pass filter
                 Tstep,         #Time step to be used in simulation. set to live to use active
                 mn=0, mx=0):   #Output saturation limits
        
        #operating variables
        self.timeOld = 0            #Variable to store old time for live calculations
        self.firstRun = True        #Tells whether or not the controller is on its first run
        self.Tstep = Tstep          #time step for simulation
        self.yold = 0               #Old value for differentiator and integrators
        self.errord1 = 0            #previous iteration error value

        #Physical system transfer coefficients
        self.a1 = a1                
        self.a0 = a0
        self.b0 = b0
        
        #output saturation limits
        self.mn = mn
        self.mx = mx
        
        #Desired closed loop characteristics
        self.wn = 2.2/tr
        self.z = z
        
        #Find controller parameters:
        self.kd = (2*z*self.wn-a1)/b0
        self.kp = (self.wn**2-a0)/b0
        self.sigma = sigma
        
        #Find DC gain of the sysetem:
        self.k = b0*self.kp/self.wn**2
        
        
        

    def update(self, ref, y):
        #Numerical Derivative
        now = 0
        if self.Tstep == live:
            now = time.time()
            Ts = now - self.timeOld
            self.timeOld = now
        else:
            Ts = self.Tstep
        
        beta =  (2.0*self.sigma-Ts)/(2.0*self.sigma+Ts) #This assumes a constant time step. Need to fix for live
        #only do derivative if there is a previous value to refference
        if self.firstRun: 
            self.firstRun = False
            self.d = 0
        else:
            self.d = beta * self.d + (1-beta)/Ts * (y - self.yold  + self.errord1)

        #save current point as the old point for next iteration
        self.yold = y

        #calculate output and return it
             
        u = (ref-y)*self.kp - self.d*self.kd   #Multipy the error by kp, subtract kd*dy
        return(saturate(u, self.mn, self.mx))

    def showParams(self):
        print("Parameters:",
              "\nkd =\t", self.kd,
              "\nkp =\t", self.kp,
              "\nk =\t",  self.k)
    
    def showCharEquation(self):
        print("Characteristic Equation:",
               "\ns**2 + ", self.a1+self.b0*self.kd,"*s + ", self.a0 + self.b0*self.kp,
               "\ns**2 + ", 2*self.wn*self.z,"*s + ", self.wn**2,
               "\nThe equations are calculated differently, but should be equivalent."  )
        
        
    def showPoles(self):  
        alph1 = 2*self.wn*self.z
        alph0 = self.wn**2
        print("Poles:\n",
              (-1*alph1 + np.sqrt(alph1**2-4*alph0))/2, "\n",
              (-1*alph1 - np.sqrt(alph1**2-4*alph0))/2)

class PDManual:
    def __init__(self, 
                 kp, kd, 
                 Tstep, 
                 mn = 0, mx = 0):
        self.kp = kp
        self.kd = kd
        self.Tstep = Tstep
        self.mn = mn
        self.mx = mx
        self.firstRun = True

    def update(self, ref, y):
        #Numerical Derivative
        now = 0
        if self.Tstep == live:
            now = time.time()

        #only do derivative if there is a previous value to refference
        if self.firstRun: 
            self.firstRun = False
            d = 0
        else:
            if self.Tstep == live:
                d = (y-self.yold)/(now-self.timeOld) #Calculate derivative based on 
                self.timeOld = now #Update time
            else:
                d = (y-self.yold)/self.Tstep 
        
        #save current point as the old point for next iteration
        self.yold = y

        #calculate output and return it      
        u = (ref-y)*self.kp - d*self.kd   #Multipy the error by kp, subtract kd*dy
        return(saturate(u, self.mn, self.mx))

class PID2ndOrderADV:#PD controller using dirty derivative
    #Physical System Transfer Function:
    #       b0
    # s**2 + a1*s + a0
    
    #Desired Reponse Parameters:
    # wn = Natural Frequency
    # z = Damping Ratio
    
    
    def __init__(self, b0, a1, a0,          #Physical System Parameters
                 tr, z, sigma,              #Derivative parameters 
                 ki, ilim,                  #integrator Parameters
                 Tstep, mn=0, mx=0):        #time step and saturation values
        #operating variables
        self.timeOld = 0            #Variable to store old time for live calculations
        self.firstRun = True        #Tells whether or not the controller is on its first run
        self.Tstep = Tstep          #time step for simulation
        self.yold = 0               #Old value for differentiator and integrators
        self.timeOld = 0            #Old value for differentiator and integrators
        self.I = 0                  #Integral
        self.timeOld = 0            #Old value for differentiator and integrators
        self.errord1 = 0            #previous iteration error value
        
        #Physical system transfer coefficients
        self.a1 = a1                
        self.a0 = a0
        self.b0 = b0
        
        #output saturation limits
        self.mn = mn
        self.mx = mx
        
        #Desired closed loop characteristics
        self.wn = 2.2/tr
        self.z = z
        
        #Find controller parameters:
        self.kd = (2*z*self.wn-a1)/b0
        self.kp = (self.wn**2-a0)/b0
        self.sigma = sigma
        self.ki = ki #integrator
        #Find DC gain of the sysetem:
        self.k = b0*self.kp/self.wn**2
        self.ilim = ilim
        
        

    def update(self, ref, y):
        #Numerical Derivative
        now = 0
        if self.Tstep == live:
            now = time.time()
            Ts = now - self.timeOld
            self.timeOld = now
        else:
            Ts = self.Tstep
        
        beta =  (2.0*self.sigma-Ts)/(2.0*self.sigma+Ts) #This assumes a constant time step. Need to fix for live
        #only do derivative if there is a previous value to refference
        if self.firstRun: 
            self.firstRun = False
            self.d = 0
        else:
            self.d = beta * self.d + (1-beta)/Ts * (y - self.yold)
        
        #Integrate
        #anti-windup
        error = ref-y
        if abs(self.d) < self.ilim: 
        # if error-self.errord1 > 0:
            self.I = self.I + (Ts/2)*(error+ self.errord1) 
        else:
            self.I = 0
        self.errord1 = (error)

        #save current point as the old point for next iteration
        self.yold = y
        
        #calculate output and return it   
        u = (ref-y)*self.kp - self.d*self.kd + self.I*self.ki   #Multipy the error by kp, subtract kd*dy
        return(saturate(u, self.mn, self.mx))

    def showParams(self):
        print("Parameters:",
              "\nkd =\t", self.kd,
              "\nkp =\t", self.kp,
              "\nk =\t",  self.k)
    
    def showCharEquation(self):
        print("Characteristic Equation:",
               "\ns**2 + ", self.a1+self.b0*self.kd,"*s + ", self.a0 + self.b0*self.kp,
               "\ns**2 + ", 2*self.wn*self.z,"*s + ", self.wn**2,
               "\nThe equations are calculated differently, but should be equivalent."  )
        
        
    def showPoles(self):  
        alph1 = 2*self.wn*self.z
        alph0 = self.wn**2
        print("Poles:\n",
              (-1*alph1 + np.sqrt(alph1**2-4*alph0))/2, "\n",
              (-1*alph1 - np.sqrt(alph1**2-4*alph0))/2)



def saturate(u, mn, mx): 
    # raise ValueError("System saturated")
    if(mn == 0 and mx == 0): # Mins and maxes weren't specified
        return(u)
    elif(u < mn):
        # print("Saturation")
        return(mn)
    elif(u > mx):
        # print("Saturation")
        return(mx)
    else:
        return(u)