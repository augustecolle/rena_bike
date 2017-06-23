import numpy as np
import matplotlib.pyplot as plt
import sys
from vector import *
import scipy
from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

sys.path.append('/home/auguste/eBike/Auguste/python/')
from HS3540 import *           #import motor data in dict HS3540

class Motor():
    def __init__(self, data):
        #data is a dictionary containing the columns of crystalyte motor data as keys and the data as values.
        self.data       = data
        self.Pe         = data['P1']     #Electrical power [W]
        self.N          = data['N']      #Rates per minute
        self.Pm         = data['P2']     #Mechanical power [W]
        self.curve2D    = np.array([[x,y] for (x, y) in zip(self.Pe, self.N)])
        self.curve3D    = np.array([[x,y,z] for (x, y, z) in zip(self.Pe, self.N, self.Pm)])
        self.points     = []
        self.ipoints    = []            #Interpolated points

    def pnt2line(cls, pnt, start, end):
        '''given a point and a start and end point of a segment, returns the distance between the nearest point on the segment and the coordinates of this point. Thus returns (dist, nearest).'''
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
        return (dist, nearest)
    
    def interpolate_line_z(cls, pnt1, pnt2, nearest):
        '''interpolates a point in the (x,y) projection of a 3d curve, returns the z-coordinate of the projected point'''
        pnt1 = np.array(pnt1)
        pnt2 = np.array(pnt2)
        x1,x2 = pnt1[0],pnt2[0]
        y1,y2 = pnt1[1],pnt2[1]
        z1,z2 = pnt1[2],pnt2[2]
        rho = np.sqrt(np.sum((pnt1-pnt2)**2))
        a = (x2-x1)/rho
        b = (y2-y1)/rho
        c = (z2-z1)/rho
        z = (nearest[0] - x1)/a*c + z1
        print(z)
        zc = (nearest[1] - y1)/b*c + z1
        print(zc)
        if (int(z) == int(zc)):
            return z
        else:
            return -1

    def PeN2Pm(cls, pnt):
        '''given a point on the (Pe, N) surface, interpolate to get Pm.'''
        pntt = (pnt[0], pnt[1], 0)
        cls.points.append(pntt)
        d = ((cls.curve2D-pnt)**2).sum(axis=1)  # compute distances
        ndx = d.argsort() # indirect sort 
        found = False
        count = -1
        while (not found):
            count = count + 1
            if (cls.curve2D[ndx[count]][0] != cls.curve2D[ndx[count + 1]][0] and cls.curve2D[ndx[count]][1] != cls.curve2D[ndx[count + 1]][1]):
                found = True
        dist, nearest = cls.pnt2line(pnt, cls.curve2D[ndx[count]], cls.curve2D[ndx[count + 1]])
        value = cls.interpolate_line_z(cls.curve3D[ndx[count]], cls.curve3D[ndx[count + 1]], nearest)
        ipoint = (nearest[0], nearest[1], value)
        cls.ipoints.append(ipoint)
        return (value)

    def plot(cls):
        #This is your data, but we're 'zooming' into just 5 data points
        #because it'll provide a better visually illustration
        #also we need to transpose to get the data in the right format
        data = np.array([cls.Pe, cls.N, cls.Pm])
        #now we get all the knots and info about the interpolated spline
        tck, u= interpolate.splprep(data)
        #here we generate the new interpolated dataset, 
        #increase the resolution by increasing the spacing, 500 in this example
        new = interpolate.splev(np.linspace(0,1,500), tck)
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter(data[0], data[1], data[2], label='originalpoints', c='Dodgerblue')
        for (x,y) in zip(cls.ipoints, cls.points):
            ax.scatter(*x, c='black', s=200)
            ax.scatter(*y, c='green', s=150)
        ax.plot(new[0], new[1], new[2], label='fit', lw =2, c='red')
        ax.set_xlabel(r'P1')
        ax.set_ylabel(r'N')
        ax.set_zlabel(r'P2')
        ax.legend()

def main():
    motor1 = Motor(HS3540)
    for x in zip(np.random.rand(1, 10)[0]*400, np.random.rand(1,10)[0]*1000):
        print(x)
        motor1.PeN2Pm(x)
    motor1.plot()
    plt.show()

if __name__ == "__main__":
    main()

