# Python Script for ENES220 Beam Project Group X
# Team Members: Jeremy Kuznetsov, Moocow

# English engineering units (lbs, in)

import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Block:
    width = 0
    height = 0
    area = 0
    centroid = 0
    cdist = 0
    def __init__(self, width, height, area, centroid):
        self.width = width
        self.height = height
        self.area = area
        self.centroid = centroid

## Change These Variables =====================================

# Measurements in in for:
web_width = 1
web_height = 1
top_flange_height = 0.5
top_flange_width = 1
bot_flange_height = 0.5
bot_flange_width = 1

# Beam Force 
F = 0

## ============================================================

# Variables for Beam Under Loading
Ra = 0
Rb = 0
Vmax = 0
Mmax = 0
SigmaMax = 0
TauMax = 0
TauGlue = 0
E = 1.8*math.pow(10,6) #units in psi, pine is 1.8*10^6, oak is 1.5*10^6
def main():
    top = Block(top_flange_width, top_flange_height, area(top_flange_width, top_flange_height), centroid(top_flange_height, web_height + bot_flange_height))
    middle = Block(web_width, web_height, area(web_width, web_height), centroid(web_height, bot_flange_height))
    bottom = Block(bot_flange_width, bot_flange_height, area(bot_flange_width, bot_flange_height), centroid(bot_flange_height, 0))

    totalheight = (top.height + middle.height + bottom.height)

    # Check for Rule Violations
    if totalheight/max(top.width,bottom.width) > 2:
        print("You have violated the height to width ratio Rule!")
    if max(top.width, bottom.width) > 2:
        print("You have violated the maximum width Rule!")
    if max(top.width/top.height, bottom.width/bottom.height) > 8:
        print("You have violated the flange Width ratio Rule!")
    if (middle.height/middle.width) > 8:
        print("You have violated the flange thickness ratio Rule!")

    totalcentroid = totalcentroidfunc(top, middle, bottom)

    top.cdist = abs(totalcentroid - (bottom.height + middle.height + (0.5*top.height)))
    middle.cdist = abs(totalcentroid - (bottom.height + (0.5*middle.height)))
    bottom.cdist = abs(totalcentroid - (0.5*bottom.height))

    totalmoment = momentsquare(top) + parallel(top) + momentsquare(middle) + parallel(middle) + momentsquare(bottom) + parallel(bottom)
    maxDeflection = -8 * 12 * F * (math.pow(20, 2) - math.pow(8, 2) - math.pow(12, 2)) / (6 * E * totalmoment * 20)  # From textbook
    xDeflection = 12  # Because its simplysupported / singleload force
    Fvalues = list(range(1000, 2500, 10))
    SigmaMaxValues = [0]*150
    TauGlueValues = [0]*150
    TauMaxValues = [0]*150

    LimitNormal = np.full(150,16000)
    LimitShear = np.full(150,3500)

    for i in range(0, 150, 1):

        Ra = (2/5)*Fvalues[i]
        Rb = (3/5)*Fvalues[i]
        Vmax = abs(Rb)
        Mmax = 12*Ra # Specific to a 20in beam loaded 12in into its length

        # Calculating Sigma Max in the Beam
        if totalcentroid > (totalheight / 2):
            SigmaMax = (Mmax * totalcentroid) / totalmoment
        else:
            SigmaMax = (Mmax * (totalheight - totalcentroid) / totalmoment)

        # Calculating Tau Max in the Beam
        TauMax = (Vmax * qmax(top, middle, bottom, totalcentroid, totalheight)) / (totalmoment * web_width)

        # Calculating the Tau Max in the Glue Areas
        if q(top) > q(bottom):
            TauGlue = (Vmax * q(top)) / (totalmoment * web_width)
        else:
            TauGlue = (Vmax * q(bottom)) / (totalmoment * web_width)

        SigmaMaxValues[i] = SigmaMax
        TauGlueValues[i] = TauGlue
        TauMaxValues[i] = TauMax

    df = pd.DataFrame.from_dict({
        'Force'            : Fvalues,
        'Max Normal Stress': SigmaMaxValues,
        'Max Shear Stress' : TauMaxValues,
        'Max Glue Stress'  : TauGlueValues,
        'Max Normal'       : LimitNormal,
        'Max Shear'        : LimitShear
    })
    
    fig, ax = plt.subplots(1)
    ax.plot(df['Force'], df['Max Normal Stress'])
    ax.plot(df['Force'], df['Max Shear Stress'])
    ax.plot(df['Force'], df['Max Glue Stress'])
    ax.plot(df['Force'], df['Max Normal'], 'red')
    ax.plot(df['Force'], df['Max Shear'], 'red')
    ax.set_title('Stresses vs. Applied Load F')
    ax.set_xlabel('Force Units (lbs)')
    ax.set_ylabel('Stress Units (psi)?')
    ax.legend(['Max Normal Stress', 'Max Shear Stress', 'Max Glue Stress'])
    #plt.show()

    ## Deflection Calculations
    Fnew = 2400
    DeflectionValues = [0]*150
    Dist = [0]*150
    min = 0

    for i in range(0,150,1):
        Dist[i] = i*(12/150)
        DeflectionValues[i] = (-Fnew*8*Dist[i])/(6*20*totalmoment*E) * (pow(20,2)-pow(8,2)-pow(Dist[i],2))
        if DeflectionValues[i] < min:
            min = DeflectionValues[i]

    dg = pd.DataFrame.from_dict({
        'Distance'   : Dist,
        'Deflection' : DeflectionValues
    })

    fig, bx = plt.subplots()
    bx.plot(dg['Distance'], dg['Deflection'])
    bx.set_title('Deflection vs Distance')
    bx.set_xlabel('Distance from left pin (in)')
    bx.set_ylabel('Displacement (in)')
    bx.legend(['Displacement'])
    plt.show()

    print(min)
    return

# Functions ============================================

def area(L1, L2):
    return L1*L2

def centroid(hgt, Offset):
    return Offset + (hgt/2)

def totalcentroidfunc(top, middle, bottom):
    atotal = top.area + bottom.area + middle.area
    return ((top.area*top.centroid) + (middle.area*middle.centroid) + (bottom.area*bottom.centroid))/atotal
    
def momentsquare(block):
    return (1/12)*block.width*math.pow(block.height, 2)

def parallel(block):
    return block.area * math.pow(block.cdist, 2)

def q(block):
    return block.area * block.cdist

def qmax(top, middle, bottom, totalcentroid, totalheight):
    q1= q(bottom) + (((totalcentroid - bottom.height) * middle.width) * (0.5*(totalcentroid - bottom.height)))
    q2 = q(top) + ((totalheight - totalcentroid - top.height) * middle.width) * (0.5 * (totalheight - totalcentroid - top.height))
    return max(q1,q2)

main()
