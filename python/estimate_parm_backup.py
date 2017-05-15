import numpy as np
import matplotlib.pyplot as plt
from vector import *

class Traject:
    def __init__(self, coords):
        '''A Traject is built of segments. Coords contains a list of (lat,lng) pairs'''
        self.segments = []
        self.num_segments = None
        self.currentS = 0
        self.dist_nextNode = None
        self.dist_currentS = None
        self.dist_nextS = None
        for i in (range(len(coords) - 1)):
            p0 = coords[i] 
            p1 = coords[i + 1]
            segment = Segment(p0, p1)
            self.segments.append(segment)
        self.num_segments = len(self.segments)

    def addMeasurements(cls, measurements):
        '''measurements is a list of Measurement class objects'''
        for obj in measurements:
            cls.addMeasurement(obj)
        return 1

    def addMeasurement(cls, measurement):
        #check if we are not on the next segment
        cls.pnt2segment(measurement)
        cls.segments[cls.currentS].addMeasurement(measurement)
        return 1

    def pnt2segment(cls, measurement):
        lat = measurement.lat
        lng = measurement.lng
        distcS = cls.dist2segment((lat, lng), cls.segments[cls.currentS])
        #check if we are not on the last segment
        if (cls.currentS + 1 < cls.num_segments):
            distnS = cls.dist2segment((lat, lng), cls.segments[cls.currentS + 1])
            newdist_nextNode = cls.dist2nextnode((lat,lng))
            if (distnS < distcS and newdist_nextNode > cls.dist_nextNode):
                cls.currentS = cls.currentS + 1
            cls.dist_nextNode = newdist_nextNode
        else: #what if we reached the last segment?
            pass

    def dist2nextnode(cls, pnt):
        lat0 = pnt[0]
        lng0 = pnt[1]
        lat1 = cls.segments[cls.currentS].p1[0]
        lng1 = cls.segments[cls.currentS].p1[1]
        return np.sqrt((lat0 - lat1)**2 + (lng0 - lng1)**2)

    def dist2segment(cls, pnt, segment):
        start = segment.p0
        end = segment.p1
        line_vec = vector(start, end)
        pnt_vec = vector(start, pnt)
        line_len = length(line_vec)
        line_unitvec = unit(line_vec)
        pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
        t = dot(line_unitvec, pnt_vec_scaled)
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        nearest = scale(line_vec, t)
        dist = distance(nearest, pnt_vec)
        nearest = add(nearest, start)
        #plt.scatter(*nearest)
        return (dist, nearest)

    @classmethod
    def fakeTraject(cls, n, x=5, y=5):
        '''make n-1 fake segments in the range [0,x), [0,y)'''
        rand_points = [(None, None)]*n
        for i in range(n):
            rand_points[i] = (np.random.random()*x, np.random.random()*y)
        #sorted_points = sorted(rand_points, key = lambda i: i[0])
        traject = cls(rand_points)
        return traject

    def fakeMeasurements(cls, n, error_gain=1):
        time = 0
        for segment in cls.segments:
            rico = (segment.p1[1]-segment.p0[1])/(segment.p1[0]-segment.p0[0])
            if (segment.p0[0] <= segment.p1[0]):
                xn = segment.p0[0] + np.random.rand(n)*abs(segment.p0[0] - segment.p1[0])
                xp = [segment.p0[0], segment.p1[0]]
                fp = [segment.p0[1], segment.p1[1]]
                xn = sorted(xn)
            elif (segment.p0[0] > segment.p1[0]):
                xn = segment.p0[0] - np.random.rand(n)*abs(segment.p0[0] - segment.p1[0])
                xp = [segment.p1[0], segment.p0[0]]
                fp = [segment.p1[1], segment.p0[1]]
                xn = sorted(xn, reverse=True)
            else:
                print("This should never be displayed, debug fakeMeasurements function")
            y = np.interp(xn, xp, fp)
            ry = [i + np.random.normal(loc=0.0, scale=0.2)*error_gain for i in y]
            for (xn, ry) in zip(xn, ry):
                time = time+1
                measurement = Measurement(time, xn, ry)
                cls.addMeasurement(measurement)
        return 1


    def plotTraject(cls):
        for x in cls.segments:
            plt.plot(*zip(*x), c=x.color)

    def plotMeasurements(cls):
        for x in cls.segments:
            x.plot()

class Segment:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.color = np.random.rand(3,1)
        self.measurements = []

    def addMeasurement(cls, measurement):
        cls.measurements.append(measurement)

    def plot(cls):
        for x in cls.measurements:
            plt.scatter(x.lat, x.lng, c=cls.color, s=200)

    def __str__(self):
        return str(self.p0) + ", " + str(self.p1)

    def __iter__(self):
        return iter([self.p0, self.p1]) 

    def __getitem__(self, value):
        if value:
            return self.p1
        elif not value:
            return self.p0
        else:
            return "index error"
 

class Measurement:
    def __init__(self, time, lat, lng):
        self.time = time
        self.lat = lat
        self.lng = lng
        self.alt = None
        self.posacc = None
        self.altacc = None
        self.speed = None
        self.heading = None
        self.amp = None
        self.volts = None
        self.windspeed = None
        self.windheading = None
        self.ci = None              #Clearness Index

    def __str__(self):
        return str(self.time) + ": " + str(self.lat) + ", " + str(self.lng)

def main(n, num, error):
   tra = Traject.fakeTraject(n)
   tra.fakeMeasurements(num, error)
   tra.plotMeasurements()
   tra.plotTraject()
   plt.show()

