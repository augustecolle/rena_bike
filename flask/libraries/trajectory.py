#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import math
import geopy
from geopy.distance import vincenty
from scipy import interpolate
import matplotlib.pyplot as plt


def get_air_density_at_height(height):
    '''using en.wikipedia.org/wiki/Density_of_air'''
    M = 0.0289644 #kg/mol
    R = 8.31447 #J/(mol K)
    L = 0.0065 #K/m
    g = 9.80665 #m/s2
    T_0 = 288.15 #K
    p_0 = 101325 #Pa
    p = p_0*(1 - L*height/T_0)**(g*M/(R*L))
    rho = p*M/(R*(T_0 - L*height))
    return rho 


class traject(object):
    '''This class contains all methods and data of a trajectory''' 

    def __init__(self):
        self.heights = []
        self.distances = []
        self.latitudes = []
        self.longitudes = []
        self.slopes = []
        self.avg_slopes = []
        self.avg_slopes_eq = []
        self.heights_c = [] #continious splines of height data
        self.compass_bearing = []
        self.rho = [] #list of air densities
        self.deltax = 0.1
        self.avg_slope_distance = 100 #slope average over number of meters


    def importGPSData(self, filename, append = False):
        '''Filename is a string containing the relative or absolute path of the GPS data file (from GPSvisualizer). Returns a list containing distances and heights of the trajectory'''
        if not append:
            self.heights = []
            self.distances = []
            self.latitudes = []
            self.longitudes = []
            self.slopes = []
        text_file = open(filename, "r")
        lines = text_file.readlines()
        #---------------Treat data---------------
        #get data only if it starts with 'T' and we should check if the list is not empty because otherwise we will get an error when trying to index the empty list in search for 'T'
        lat_long_alt = [x.split()[1:] for x in lines if (len(x.split()) == 4 and x.split()[0] == 'T')] 
        #convert string to floating point values
        self.latitudes = np.array([float(x[0]) for x in lat_long_alt])
        self.longitudes = np.array([float(x[1]) for x in lat_long_alt])
        self.heights = np.array([float(x[2]) for x in lat_long_alt])
        latitudesMask = np.array([True if not (self.latitudes[x] == self.latitudes[x+1]) else False for x in range(len(self.latitudes)-1)])
        longitudesMask = np.array([True if not (self.latitudes[x] == self.latitudes[x+1]) else False for x in range(len(self.latitudes)-1)])
        heightsMask = np.array([True if not (self.latitudes[x] == self.latitudes[x+1]) else False for x in range(len(self.latitudes)-1)])
        #only delete a point if it is equal in height, lat and long (redundant information)
        doublepoints = np.array([all(t) for t in zip(longitudesMask, latitudesMask, heightsMask)])
        self.latitudes = self.latitudes[doublepoints]
        self.longitudes = self.longitudes[doublepoints]
        self.heights = self.heights[doublepoints]
        #---------------Calculate distances between lats en longs---------------
        start = tuple([self.latitudes[0], self.longitudes[0]])
        i = 1
        for x in zip(self.latitudes[1:], self.longitudes[1:]):
            dist = vincenty(x, start).meters
            if dist > 0:
                self.distances.append(dist)
            else:
                self.distances.append(1e-9)
                #self.distances.append(1e-9) #if we would end up somehow by having twice the same point (can't devide by zero)
            start = x
            i = i + 1
        self.get_air_densities()
        self.pretty_printing_lat_long()
        return 0

    def get_air_densities(self):
        '''using en.wikipedia.org/wiki/Density_of_air'''
        self.rho = []
        M = 0.0289644 #kg/mol
        R = 8.31447 #J/(mol K)
        L = 0.0065 #K/m
        g = 9.80665 #m/s2
        T_0 = 288.15 #K
        p_0 = 101325 #Pa
        for h in self.heights:
            p = p_0*(1 - L*h/T_0)**(g*M/(R*L))
            rho = p*M/(R*(T_0 - L*h))
            self.rho.append(rho)
        return self.rho 
   

    def get_startPosition(self):
        if (len(self.latitudes) == 0):
            print("No trajectory loaded") 
            return -1
        return [self.latitudes[0], self.longitudes[0]]


    def get_slopes(self, deltax = None):
        '''Input is a datadict gotten from importGPSData, it contains the heights and distances of a trajectory. Returns a list with the slopes for the trajectory'''
        if deltax == None: deltax = self.deltax
        #we need difference in height for two points since we want the slope between these points
        height_diff = np.array([(self.heights[x] - self.heights[x-1]) for x in range(1, len(self.heights))]) 
        slopes = [y/x*100 for y,x in zip(height_diff, self.distances)] #calculate slope in percentages
        #print(max(slopes), min(slopes)) #check maxima
        cum_distances = np.cumsum(self.distances)
        slope_index = cum_distances*1.0/deltax #slope index for advancing slope_avg_distance
        slope_index = np.insert(slope_index, 0, 0)
        x = cum_distances
        y = np.cumsum(height_diff)
        #determining smoothing factor according to the docs: (m - sqrt(2*m)) * std**2 <= s <= (m + sqrt(2*m)) * std**2 but this gives an horrible over smoothing so I am choosing my own
        tck = interpolate.splrep(x, y, s=30) #used to be 40 for the profile with loads of data
        xnew = np.arange(0, cum_distances[-1], deltax)
        self.heights_c = interpolate.splev(xnew, tck, der=0)
        self.slopes =  interpolate.splev(xnew, tck, der=1)
        self.avg_slopes = [self.slopes[slope_index[x]:slope_index[x+1]].mean() for x in range(len(slope_index)-1)]
        return self.avg_slopes    


    def get_eq_dist_slopes(self, deltax = None, avg_slope_distance = None):
        '''Input is a datadict gotten from importGPSData, it contains the heights and distances of a trajectory. Returns a list with the slopes for the trajectory'''
        if deltax == None: deltax = self.deltax
        if avg_slope_distance == None:
            avg_slope_distance = self.avg_slope_distance
        else:
            self.avg_slope_distance = avg_slope_distance
        #we need difference in height for two points since we want the slope between these points
        height_diff = np.array([(self.heights[x] - self.heights[x-1]) for x in range(1, len(self.heights))]) 
        slopes = [y/x*100 for y,x in zip(height_diff, self.distances)] #calculate slope in percentages
        #print(max(slopes), min(slopes)) #check maxima
        cum_distances = np.cumsum(self.distances)
        slope_index = int(avg_slope_distance*1.0/deltax) #slope index for advancing slope_avg_distance
        x = cum_distances
        y = np.cumsum(height_diff)
        #determining smoothing factor according to the docs: (m - sqrt(2*m)) * std**2 <= s <= (m + sqrt(2*m)) * std**2 but this gives an horrible over smoothing so I am choosing my own
        tck = interpolate.splrep(x, y, s=10) #used to be 40 for the profile with loads of data
        xnew = np.arange(0, cum_distances[-1], deltax)
        self.heights_c = interpolate.splev(xnew, tck, der=0)
        self.slopes =  interpolate.splev(xnew, tck, der=1)
        self.avg_slopes_eq = [self.slopes[x*slope_index:x*slope_index+slope_index].mean() for x in range(len(xnew)/slope_index+1)]
        return self.avg_slopes_eq    


    def get_compass_bearing(self):
        """
        Calculates the bearing between two points.
        The formulae used is the following:
            θ = atan2(sin(Δlong).cos(lat2),
                      cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
        Latitude and longitude must be in decimal degrees
        :Returns:
          The bearing in degrees
        :Returns Type:
          float
        """
        self.compass_bearing = []
        for i in range(len(self.latitudes)-1):
            lat1 = math.radians(self.latitudes[i])
            lat2 = math.radians(self.latitudes[i+1])
            diffLong = math.radians(self.longitudes[i+1] - self.longitudes[i])
            x = math.sin(diffLong) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
            initial_bearing = math.atan2(x, y)
            # Now we have the initial bearing but math.atan2 return values
            # from -180° to + 180° which is not what we want for a compass bearing
            # The solution is to normalize the initial bearing as shown below
            initial_bearing = math.degrees(initial_bearing)
            compass_bearing = (initial_bearing + 360) % 360
            self.compass_bearing.append(compass_bearing)
        return self.compass_bearing

    
    def pretty_printing_dist_comp(self):
        fmt = '%-8s%-20s%s'
        print(fmt % ('', 'Distances', 'Compass bearing'))
        for i, (distance, degree) in enumerate(zip(self.distances, self.compass_bearing)):
            print(fmt % (i, distance, degree))
        return 0
     

    def pretty_printing_lat_long(self):
        fmt = '%-8s%-20s%-20s%s'
        print(fmt % ('', 'Latitudes', 'Longitudes', 'heights'))
        for i, (lat, long, height) in enumerate(zip(self.latitudes, self.longitudes, self.heights)):
            print(fmt % (i, lat, long, height))
        return 0
        
    
    def slope_plot_on_current_axis(self):
        cum_distances = np.cumsum(self.distances)
        cum_distances = np.insert(cum_distances, 0, 0)
        xnew = np.arange(0, np.cumsum(self.distances)[-1], self.deltax)
        fig, ax1 = plt.gcf(), plt.gca()
        ax1.plot(xnew, self.heights_c + self.heights[0], color='black')
        ax1.plot(np.cumsum(self.distances), self.heights[1:], 'x')
        ax2 = ax1.twinx()
        ax2.plot(xnew, self.slopes, color='red')
        ax2.bar(cum_distances[:-1], self.avg_slopes, color='green', width=np.array(self.distances), alpha=0.3)
        return 0


    def simple_slope_plot(self):
        cum_distances = np.cumsum(self.distances)
        cum_distances = np.insert(cum_distances, 0, 0)
        xnew = np.arange(0, np.cumsum(self.distances)[-1], self.deltax)
        fig, ax1 = plt.subplots()
        ax1.plot(xnew, self.heights_c + self.heights[0], color='black')
        ax1.plot(np.cumsum(self.distances), self.heights[1:], 'x')
        ax2 = ax1.twinx()
        ax2.plot(xnew, self.slopes, color='red')
        ax2.bar(cum_distances[:-1], self.avg_slopes, color='green', width=np.array(self.distances), alpha=0.3)
        plt.show()


    def integrated_slope_plot(self, avg_slope_distance = None):
        '''I think I made this unnecessary complicated, I will correct this in the near future'''
        if avg_slope_distance == None: avg_slope_distance = self.avg_slope_distance
        slope_index = int(avg_slope_distance*1.0/self.deltax) 
        xnew = np.arange(0, np.cumsum(self.distances)[-1], self.deltax)
        fig, ax1 = plt.subplots()
        ax1.plot(xnew, self.heights_c + self.heights[0], color='black')
        ax1.plot(np.cumsum(self.distances), self.heights[1:], 'x')
        ax2 = ax1.twinx()
        ax2.plot(xnew, self.slopes, color='red')
        ax2.bar([xnew[x*slope_index] for x in range(len(xnew)/slope_index+1)], self.avg_slopes_eq, color='green', width=slope_index*self.deltax, alpha=0.3)
        plt.show()


