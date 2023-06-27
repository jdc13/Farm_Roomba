/*This file contains a controller for the wall follow algorithm
Created by: Josh Chapman
April 3, 2023*/

//For simulation:


using namespace std;

#ifndef WALLFOLLOW.H
#define WALLFOLLOW.H

#include <cmath>

#define simulation

float v;
float d;

float Obs[3]; //Data storage for the observer
//X, Y, Theta

#ifndef simulation
    float Ts;
#else
    //For simulation:
    float Ts = 0.001;
#endif




struct {
  int myNum;
  float myString;
} myStruct1;






//Physical paramters of the robot
float L = 12; //Distance between wheels


float saturate(float u, float mn, float mx){
    if(u < mn){
        return mn;
    }
    else if(u > mx){
        return mx;
    }
    else{
        return u;
    }
}


class PD2ndOrderADV{ //This class is based on the class of the same name in the python controllers file.
    public:
    //Operating Variables:
    float timeOld = 0;      //Old time for live calculations
    bool firstRun = true;   //tells whether or not to use the derivative
    float yold = 0;         //Old value for differentiator
    float errord1 = 0;      //Old value for differentiator
    
    //Saturation limits
    float mn = 0;
    float mx = 0;


    //Gains:
    float kd;
    float kp;

    //operating values:
    float sigma;
    //Constructor
    void init(float b0, float a1, float a0, float tr, float z, float sigma_d){
        /*Plant Transfer Function
               b0
        s^2 + a1*s + a0  */
        /*Desired controlled parameters:
        tr = rise time
        wn = natural frequency
        z = damping ratio*/

        //Calculate controller parameters:
        float wn = 2.2/tr;
        kd = (2*z*wn-a1)/b0;
        kp = (wn*wn-a0)/b0;
        sigma = sigma_d;
    }

    //Update:
    float update(float ref, float y){

        #ifndef simulation
            float now = milis(); //For arduino
            Ts = now - timeOld;
        #endif

        float beta = (2*sigma-Ts)/(2*sigma+Ts);

        //Only do the derivative if there is a previous value to refference
        float d = 0;//derivative value

        if(firstRun){
            firstRun = false;
        }
        else{
            d = beta * d + (1-beta)/Ts * (y - yold + errord1);
        }

        //Save current values for next iteration
        yold = y;
        errord1 = ref-y;
        
        // For arduino:
        #ifndef simulation
            timeOld = now;  
        #endif

        //Calculate output
        float u = (ref-y)*kp - d*kd;  
        return u;

    }


    

};


class WallFollow{
    public:
    //Saturation Limits
    float vmax;
    float vmin;
    float Dmax;
    float Dmin;
    float ThetaMax;
    float ThetaMin;

    //low pass filter parameter
    float sigma = 0.1;    

    //Controller:
    PD2ndOrderADV WF;


    //Constructor:
    WallFollow(float tr, float zeta, float v, float D, float theta){
       //Physical System Transfer Function:
        vmax = v;
        vmin = v*-1;

        float b0 = vmax/L;
        float a0 = 0;
        float a1 = 0;
        
        // Initialize controller:
        //      Plant Xfer Function     Rise Time   Damping Ratio   Filter param
        WF.init(b0, a1, a0,             .5,         .707,           .01);

    }

    float update(float target){
        d = WF.update(target, Obs[1]);//Run controller based on y

        if(abs(Obs[2])>ThetaMax*4/5){
            v = vmax;
        }
        else{
            v = vmax - (vmax-vmin)*(abs(d)/Dmax);
        }

        // Calculate distances traveled
        float dy = v * sin(Obs[2])*Ts;
        float dx = v * cos(Obs[2])*Ts;
        float dtheta = d/L * Ts;

        //Update observer:
        Obs[0] += dx;
        Obs[1] += dy;
        Obs[2] += dtheta;

        // This function edits global variables, so nothing to return.

    }

    
    
    
};


#endif