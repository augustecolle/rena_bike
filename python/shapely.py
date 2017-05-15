import numpy as np
import matplotlib.pyplot as plt
from vector import *


class Traject:
    def __init__(self, coords):
        '''A Traject is built of segments. Coords contains a list of (lat,lng) pairs'''
        self.segments = []
        self.measurements = [] 
        self.assigned_mts = {}
        for i in (range(len(coords) - 1)):
            p0 = coords[i] 
            p1 = coords[i + 1]
            segment = Segment(p0, p1)
            self.segments.append(segment)

    @classmethod
    def fake_traject(cls, n, x=5, y=5):
        '''make n-1 fake segments in the range [0,x), [0,y)'''
        rand_points = [(None, None)]*n
        for i in range(n):
            rand_points[i] = (np.random.random()*x, np.random.random()*y)
        sorted_points = sorted(rand_points, key = lambda i: i[0])
        traject = cls(sorted_points)
        return traject

    def add_fake_measurements(cls, n, x=5, y=5, error_gain=1):
        cls.plot_traject()
        xn = sorted(np.random.rand(n)*x)
        xp = [i[0][0] for i in cls.segments]
        fp = [i[0][1] for i in cls.segments]
        #append last coordinate
        xp.append(cls.segments[-1][1][0])
        fp.append(cls.segments[-1][1][1])
        y = np.interp(xn, xp, fp)
        ry = [i + np.random.normal(loc=0.0, scale=0.2)*error_gain for i in y]
        measurements = []
        for (xn, ry) in zip(xn, ry):
            measurements.append((xn, ry))
            plt.scatter(xn, ry, s=150)
        cls.measurements = measurements
        return measurements
    
    def test_dist(cls):
        p = (1,1)
        plt.scatter(*p)
        for x in cls.segments:
            cls.pnt2segment(p, x)
        cls.plot_traject()

    def assign_pnts(cls, pointlist):
        '''assign points to trajectory segments, pointlist is a list of (lat,lng) points'''
        plt.cla()
        segments_num = len(cls.segments)
        segment_count = 2
        time = 0 #use timestamp as key in the future
        cls.assigned_mts[cls.segments[segment_count]] = [] 
        color = np.random.rand(3,1)
        dist1_flag = False
        dist2_flag = False
        dist3_flag = False
        for pnt in pointlist:
            time = time + 1
            dist1, nearest1 = cls.pnt2segment(pnt, cls.segments[segment_count - 2])
            dist2, nearest2 = cls.pnt2segment(pnt, cls.segments[segment_count - 1])
            dist3, nearest3 = cls.pnt2segment(pnt, cls.segments[segment_count - 0])
            if (dist1 < dist2 and dist1 < dist3):
                if (not dist1_flag):
                    print("DIST1")
                    print(dist1)
                    print(dist2)
                    print(dist3)
                    dist3_flag = False
                    dist2_flag = False
                    dist1_flag = True
            elif (dist2 < dist1 and dist2 < dist3):
                if (not dist2_flag):
                    print("DIST2")
                    print(dist1)
                    print(dist2)
                    print(dist3)
                    dist3_flag = False
                    dist2_flag = True
                    dist1_flag = False
                    color = np.random.rand(3,1)
                if (segment_count < segments_num - 1):
                    segment_count = segment_count + 1
                    cls.assigned_mts[cls.segments[segment_count]] = [] 
            elif (dist3 < dist1 and dist3 < dist2):
                if (not dist3_flag):
                    print("DIST3")
                    print(dist1)
                    print(dist2)
                    print(dist3)
                    dist3_flag = True
                    dist2_flag = False
                    dist1_flag = False
                    color = np.random.rand(3,1)
                if (segment_count < segments_num - 2):
                    segment_count = segment_count + 2
                    cls.assigned_mts[cls.segments[segment_count]] = [] 
            plt.scatter(*pnt, s = 220, c=color)
            cls.assigned_mts[cls.segments[segment_count]].append({time: pnt}) 
        cls.plot_traject()
        return cls.assigned_mts

    @classmethod
    def pnt2segment(cls, pnt, segment):
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


    def plot_traject(cls):
        for x in cls.segments:
            plt.plot(*zip(*x))

    def __str__(cls):
        string = ""
        for x in cls.segments:
            string = string + str(x) + "\n"
        return string

class Segment:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
    

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
 
    def rand_points_around_segments(n, segments, error_magn=1):
        '''returns n random points around a list of segments. Error_magn is optional and determines the maximum deviation of the random points from the interpolated points'''
        x = np.linspace(segments[0][0], segments[-1][0], n)
        xp = [i[0] for i in segments]
        fp = [i[1] for i in segments]
        y = np.interp(x, xp, fp)
        rand_y = [i + np.random.normal(loc=0.0, scale=0.2)*error_magn for i in y]
        return zip(x, rand_y)
    
    
    def dist_point_to_segment(point, segment):
        '''returns the distance of the point (x,y) to a segment which is a list of 2 point coordinates'''
        (x0, y0) = segment[0]
        (x1, y1) = segment[1]
        (xp, yp) = point
        #https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points
        dist = np.abs((y1-y0)*xp - (x1-x0)*yp + x1*y0 - y1*x0)/(np.sqrt((y1-y0)**2 + (x1-x0)**2))
        return dist

#
#def main():
#    segments = random_segments(10, 5, 5)
#    rand_points = rand_points_around_segments(100, segments)
#    count = 0
#    flag = 0
#    color = np.random.rand(3,1)
#    for point in rand_points:
#        if (count + 3 < len(segments)):
#            dist1 = dist_point_to_segment(point, segments[count:count+2])
#            dist2 = dist_point_to_segment(point, segments[count+1:count+3])
#        elif (flag == 0):
#            color = np.random.rand(3,1)
#            flag = 1
#        if (dist2 < dist1 and count + 3 < len(segments)):
#            color = np.random.rand(3,1)
#            count = count + 1
#            print(count)
#        plt.scatter(*point, c=color, s=120)
#    #first unpack the list, giving tuples, then zip to (xcoords, ycoords), then unpack for scatter
#    #plt.scatter(*zip(*rand_points))
#    plt.plot(*zip(*segments))
#    plt.show()

