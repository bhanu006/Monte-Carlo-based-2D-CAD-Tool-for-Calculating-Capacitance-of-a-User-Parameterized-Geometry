################################################################################
# Copyright (c) 2021, Shiv Nadar University, Delhi NCR, India. All Rights
# Reserved. Permission to use, copy, modify and distribute this software for
# educational, research, and not-for-profit purposes, without fee and without a
# signed license agreement, is hereby granted, provided that this paragraph and
# the following two paragraphs appear in all copies, modifications, and
# distributions.
#
# IN NO EVENT SHALL SHIV NADAR UNIVERSITY BE LIABLE TO ANY PARTY FOR DIRECT,
# INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
# PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE.
#
# SHIV NADAR UNIVERSITY SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS PROVIDED "AS IS". SHIV
# NADAR UNIVERSITY HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
# ENHANCEMENTS, OR MODIFICATIONS.
#
# Revision History:
# Date          By                     Change Notes
# ------------ ---------------------- ------------------------------------------
# Apr 25th 2022 Bhavith & Bhanoday     Log file is added to store the output
#                                      capacitance value.
# 
# Apr 17th 2022 Bhavith & Bhanoday     Updated .Json configuration file to .ini 
#                                      configuration file to make it a 
#                                      human-readable text format.  
#
# Apr 10th 2022 Bhavith & Bhanoday     Json Configuration file is created to
#                                      give multiple sets of input.
#
# Mar 25th 2022 Bhavith & Bhanoday     Added new parameter Angle of the 
#                                      upper plate.
#
# Feb 28th 2022 Bhavith & Bhanoday     Found a bug in Final Voltage function        
#                                      and fixed it.
#
# Dec 12th 2021 Bhavith & Bhanoday     Updated FRW and Final_voltage functions
#                                      for better performance.
#
# Dec  2nd 2021 Bhavith & Bhanoday     Modified code to take user defined inputs
#
# Nov 25th 2021 Bhavith & Bhanoday     Found another bug in distance function
#                                      Random walk stuck in infinite loop and
#                                      returned nan values. Fixed it.
#
# Nov 14th 2021 Bhavith & Bhanoday     Fixed a bug in Distance function.
#
# Oct 26th 2021 Bhavith & Bhanoday     Original
#
################################################################################

'''Monte Carlo based 2D CAD Tool for Calculating Capacitance of a User-Parameterized Geometry 
and Validated against a Golden Reference'''

# Importing Required Libraries
import math
import random
from collections import Counter
import configparser
import logging

# Function for finding minimum distance between given point and rectangular plate
def distance_rect_point(x, y, x_min, y_min, x_max, y_max):
    r = 0
    if(x <= x_min):
        if(y <= y_min):
            r = (math.dist([x,y],[x_min,y_min]))
            return r
        elif(y >= y_max):
            r = (math.dist([x,y],[x_min,y_max]))
            return r
        elif((y > y_min) and (y < y_max)):
            r = (x_min - x)
            return r

    if((x > x_min) and (x < x_max)):
        if(y <= y_min):
            r = (y_min - y)
            return r
        elif(y >= y_max):
            r = (y - y_max)
            return r
        elif((y > y_min) and (y < y_max)):
            return 0

    if(x >= x_max):
        if(y <= y_min):
            r = (math.dist([x,y],[x_max,y_min]))
            return r
        elif(y >= y_max):
            r = (math.dist([x,y],[x_max,y_max]))
            return r
        elif((y > y_min) and (y < y_max)):
            r = (x - x_max)
            return r

# Function for calculating the minimum distance between a given point and inclined upper plate.
def angle_dist(angle_up,x,y):
    x1 = x-(x1_min+(length_up/2))
    y1 = y-(y1_max+space+(thickness_up/2))
    x_new = x1*(round(math.cos(math.radians(angle_up)),2)) - y1*(round(math.sin(math.radians(angle_up)),2))
    y_new = x1*(round(math.sin(math.radians(angle_up)),2)) + y1*(round(math.cos(math.radians(angle_up)),2))
    distance = distance_rect_point(x_new, y_new, x2_min, y2_min, x2_max, y2_max)
    return distance


#Function for calculating maximum radius of the circle which dosen't cross the boundary of geometry
def max_radius(x,y):
    a = distance_rect_point(x, y, x1_min, y1_min, x1_max, y1_max) # Distance from a point to the lower rectangular plate
    b = angle_dist(angle_up,x,y) # Distance from a point to the upper rectangular plate
    r = min(a,b)
    return r

# Function for generating random point on circumference of the circle
def random_walk(x,y,r):
    k = random.randint(0,360)         # Assigns random polar angle between 0 to 360 degrees
    x_new = x + r*(round(math.cos(math.radians(k)),2)) # x coordinate of new random point
    y_new = y + r*(round(math.sin(math.radians(k)),2)) # y coordinate of new random point
    return (x_new, y_new)                              # new random point


#Floating Random Walk Algorithm
def FRW(point):
    while True:
        r = max_radius(point[0], point[1])
        point = random_walk(point[0], point[1], r)
        x, y = point
        d1 = distance_rect_point(x, y, x1_min, y1_min, x1_max, y1_max)
        d2 = angle_dist(angle_up,x,y)
        
        try:
            if d2 <= DEL:
                return R2_VOLTAGE             # Terminating condition for Floating Random Walk Algorithm
            if d1 <= DEL:
                return R1_VOLTAGE
        except:
            return


# Function for calculating voltage at a given point
def Final_voltage(point):
    iters = 10                                    # Initializing number of iterations
    voltages = []
    for i in range(iters):
        voltages.append(FRW(point))               # Storing new voltage value after every iteration
    voltages_dict = dict(Counter(voltages))
    voltage_keys = list(voltages_dict.keys())

    try:
        up_count = voltages_dict[voltage_up]
    except:
        up_count = 0

    try:
        lp_count = voltages_dict[voltage_lp]
    except:
        lp_count = 0
        
    voltages_dict = {voltage_up:up_count, voltage_lp:lp_count}
            
    final_voltage = (lp_count*voltages_dict[voltage_lp] + up_count*voltages_dict[voltage_up])/ (up_count+lp_count) # Average Voltage of all iterations
    return final_voltage

#Calculation of Electric Field around the upper rectangular plate

#Total Electric Field is divided into four parts :
#EF_down() = Electric field in the downward region of the upper plate
#EF_up() = Electric field in the upward region of the upper plate
#EF_left() = Electric field in the leftward region of the upper plate
#EF_right() = Electric field in the rightward region of the upper plate

def EF_down():                   
    down = 0
    x_v1 = x1_min
    y_v1 = y1_min - t
    x_v2 = x1_min
    y_v2 = y1_min - 2*t
    while x_v1 < x1_max :
        p1 = (x_v1,y_v1)
        p2 = (x_v2,y_v2)
        v1 = Final_voltage(p1) 
        v2 = Final_voltage(p2)
        Electric_Field = (abs(v1-v2))/t
        down = down + Electric_Field
        x_v1 = x_v1+t
        x_v2 = x_v2+t
    return down

def EF_up():
    up = 0
    x_v1 = x1_min
    y_v1 = y1_max + t
    x_v2 = x1_min
    y_v2 = y1_max + 2*t
    while x_v1 < x1_max :
        p1 = (x_v1,y_v1)
        p2 = (x_v2,y_v2)
        v1 = Final_voltage(p1)
        v2 = Final_voltage(p2)
        Electric_Field = (abs(v1-v2))/t
        up = up + Electric_Field
        x_v1 = x_v1+t
        x_v2 = x_v2+t
    return up

def EF_left():
    left = 0
    x_v1 = x1_min-t
    y_v1 = y1_min
    x_v2 = x1_min-2*t
    y_v2 = y1_min
    while y_v1 < y1_max :
        p1 = (x_v1,y_v1)
        p2 = (x_v2,y_v2)
        v1 = Final_voltage(p1)
        v2 = Final_voltage(p2)
        Electric_Field = (abs(v1-v2))/t
        left = left + Electric_Field
        y_v1 = y_v1+t
        y_v2 = y_v2+t
    return left

def EF_right():
    right = 0
    x_v1 = x1_max+t
    y_v1 = y1_min
    x_v2 = x1_max+2*t
    y_v2 = y1_min
    while y_v1 < y1_max :
        p1 = (x_v1,y_v1)
        p2 = (x_v2,y_v2)
        v1 = Final_voltage(p1)
        v2 = Final_voltage(p2)
        Electric_Field = (abs(v1-v2))/t
        right = right + Electric_Field
        y_v1 = y_v1+t
        y_v2 = y_v2+t
    return right

#Function for calculating the Capacitance
def capacitance():
    down = EF_down()
    Total_EF = (down + EF_up() + EF_right() + EF_left())
    Charge = Total_EF * t * E
    TotalCap = Charge/(R2_VOLTAGE - R1_VOLTAGE)
    downcap  = down*t*E
    return TotalCap,downcap

formatter = logging.Formatter('%(asctime)s %(message)s',"%Y-%m-%d %H:%M:%S") #FORMAT of log message
#Function to setup the log files
def setup_logger(name, log_file, level=logging.DEBUG): 
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter) 
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(streamHandler)
    return logger

config = configparser.ConfigParser()  #ConfigParser() is responsible for parsing a list of configuration files

config.read('Configuration Files/config_angle.ini')  # Reads the specified Configuration file

# The for loop loads input data from each section of the Configuration file
for section in config.sections():
    length_up = float(config.get(section, "length_up"))        # Length of the upper plate in um
    thickness_up = float(config.get(section, "thickness_up"))  # Thickness of the upper plate in um
    angle_up = float(config.get(section, "angle_up"))          # Angle at which the upper plate is rotated in degrees
    voltage_up = float(config.get(section, "voltage_up"))      # Voltage of the upper plate in Volts
    length_lp = float(config.get(section, "length_lp"))        # Length of the lower plate in um
    thickness_lp = float(config.get(section, "thickness_lp"))  # Thickness of the lower plate in um
    voltage_lp = float(config.get(section, "voltage_lp"))      # Voltage of the lower plate in Volts
    space = float(config.get(section, "space"))                # Distance between the plates in um
    Er = float(config.get(section, "Er"))                      # Dielectric Constant of the medium
    out_file = config.get(section, "SetNameOutput")            # Output file 
    
    R1_VOLTAGE = voltage_lp             # Voltage of lower rectangular plate
    R2_VOLTAGE = voltage_up             # Voltage of upper rectangular plate

    x1_min = 0
    y1_min = 0
                                # Coordinates of Lower Plate                   
    x1_max = x1_min + length_lp
    y1_max = y1_min + thickness_lp
                                
    x2_min = -(length_up/2)
    y2_min = -(thickness_up/2)
                                        # Coordinates of Upper Plate                      
    x2_max = length_up/2
    y2_max = thickness_up/2
    
    #Terminating distance value for Floating Random Walk Algorithm
    DEL = min(length_up,thickness_up,length_lp,thickness_lp,space)/1000 
    t = min(length_up,thickness_up,length_lp,thickness_lp,space)/100        

    E = Er*(8.8541*pow(10,-12))    # Permittivity of the medium 


    Capacitance = capacitance() #Calculates the required Capacitance

    # Initializing the output log file
    logger = setup_logger(out_file, f"logs/{out_file}.log", logging.DEBUG)
    logger.info("Capacitance Value for {} in (aF/um): {}".format(section, round(Capacitance[0] * pow(10,12),2)))
  




