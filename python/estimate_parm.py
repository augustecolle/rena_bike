import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/auguste/eBike/Auguste/python/')
from vector import *
import MySQLdb
import gmplot
import scipy.optimize
import pylab as pl
import par_est_cam as cc

np.seterr(divide='ignore', invalid='ignore')
#prediction database:
#index ID traject_ID latitude longitude heading height slope

class Traject:
    def __init__(self, data):
        '''A Traject is built of segments. Data contains a list of dictionaries with keys latitude, longitude, heading, height and slope'''
        self.segments = []
        self.num_segments = None
        self.currentS = 0
        self.dist_nextNode = None
        self.dist_currentS = None
        self.dist_nextS = None
        self.weight = None
        for i in (range(len(data) - 1)):
            p0 = data[i] 
            p1 = data[i + 1]
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

    
    def addWeight(cls, weight):
        cls.weight = weight
        return cls.weight


    def plotFakeTraject(cls):
        for x in cls.segments:
            plt.plot(*zip(*x), c=x.color)

    def plotTraject(cls):
        for x in cls.segments:
            plt.plot(*zip(x.p0, x.p1), c=x.color)

    def plotMeasurements(cls):
        for x in cls.segments:
            x.plot()

    def plotMeasurementsOnMap(cls):
        lats = []
        longs = []
        gmap = gmplot.GoogleMapPlotter(51.06, 3.71, 16)
        #gmap.plot(lats, longs, 'cornflowerblue', edge_width=10)
        for x in cls.segments:
            for y in x.measurements:
                lats.append(y.lat)
                longs.append(y.lng)
        gmap.scatter(lats, longs, '#3B0B39', size=1, marker=False)
        #gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
        gmap.heatmap(lats, longs)
        gmap.draw("measurements.html")
        print("DONE")

    def  plot_vc(cls):
        '''plot velocity of cyclist over the traject'''
        for seg in cls.segments:
            seg.plot_vc()

    def  plot_power(cls):
        '''plot velocity of cyclist over the traject'''
        for seg in cls.segments:
            seg.plot_power()


    def  plot_va(cls):
        '''plot velocity of cyclist over the traject'''
        for seg in cls.segments:
            seg.plot_va()


    def plotTrajectOnMap(cls, name="traject.html"):
        lats = []
        longs = []
        for seg in cls.segments:
            lats.append(seg.p0[0])
            longs.append(seg.p0[1])
        gmap = gmplot.GoogleMapPlotter(51.06, 3.71, 16)
        #gmap.plot(lats, longs, 'cornflowerblue', edge_width=10)
        gmap.scatter(lats, longs, '#3B0B39', size=1, marker=False)
        #gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
        gmap.heatmap(lats, longs)
        gmap.draw(name)
        print("DONE")



class Segment:
    def __init__(self, pr0, pr1):
        '''pr is a prediction, a dictionary containing lat, lng, heading, height and slope'''
        self.p0 = (pr0['latitude'], pr0['longitude'])
        self.p1 = (pr1['latitude'], pr1['longitude'])
        self.slope = pr0['slope']
        self.height0 = pr0['height']
        self.height1 = pr1['height']
        self.heading = pr0['heading']
        self.color = np.random.rand(3,1)
        self.measurements = []
        self.rho = self.getRho()

    def getRho(cls):
        '''using en.wikipedia.org/wiki/Density_of_air'''
        M = 0.0289644 #kg/mol
        R = 8.31447 #J/(mol K)
        L = 0.0065 #K/m
        g = 9.80665 #m/s2
        T_0 = 288.15 #K
        p_0 = 101325 #Pa
        height = (cls.height0 + cls.height1)/2.0
        p = p_0*(1 - L*height/T_0)**(g*M/(R*L))
        cls.rho = p*M/(R*(T_0 - L*height))
        return cls.rho 

    def addMeasurement(cls, measurement):
        cls.measurements.append(measurement)

    def plot(cls):
        for x in cls.measurements:
            plt.scatter(x.lat, x.lng, c=cls.color, s=200)

    def plot_vc(cls):
        '''plot velocity of cyclist on segment'''
        for x in cls.measurements:
            plt.scatter(x.time, x.speed, c=cls.color, s=50)

    def plot_power(cls):
        for x in cls.measurements:
            plt.scatter(x.time, x.amps*x.volts, c=cls.color, s=50)

    def plot_va(cls):
        '''plot velocity of cyclist on segment'''
        for x in cls.measurements:
            plt.scatter(x.time, x.windspeed, c=cls.color, s=200)

    def plot_heading(cls):
        for x in cls.measurements:
            plt.scatter(x.time, x.heading, c=cls.color, s=200)

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
    def __init__(self, time, lat, lng, alt=None, posacc=None, altacc=None, speed=None, heading=None, amps=None, volts=None, windspeed=None, windheading=None, ci=None, weight=None):
        self.time = time
        self.lat = lat
        self.lng = lng
        self.alt = alt
        self.posacc = posacc
        self.altacc = altacc
        self.speed = speed
        self.heading = heading
        self.amps = amps
        self.volts = volts
        self.windspeed = windspeed
        self.windheading = windheading
        self.prvwsigned = self.getProjectedvw()
        self.ci = ci                    #Clearness Index
        self.weight = weight

    def getProjectedvw(cls):
        alpha = (90 - (cls.windheading - 180))*np.pi/180.0
        beta = (450 - cls.heading)*np.pi/180.0
        if (cls.speed == 0):
            cls.speed = 1e-3
        v_wind = cls.windspeed #already in m/s
        v_w = np.array([v_wind*np.cos(alpha), v_wind*np.sin(alpha)])
        v_f = np.array([cls.speed*np.cos(beta), cls.speed*np.sin(beta)])
        v_weq = v_w - v_f
        v_weq_mag = np.sqrt(v_weq[0]**2 + v_weq[1]**2)
        cls.sqprvwsigned = (v_weq_mag**2*np.cos(np.arccos(np.clip(np.dot(v_f/np.linalg.norm(v_f), v_weq/np.linalg.norm(v_weq)), -1.0, 1.0)))) #projected windspeed
        if (np.isnan(cls.sqprvwsigned)):
            print('NAN')
            #print(v_f)
            #print(v_w)
        return cls.sqprvwsigned

    def __str__(self):
        return str(self.time) + ": " + str(self.lat) + ", " + str(self.lng)

def test(n, num, error):
   tra = Traject.fakeTraject(n)
   tra.fakeMeasurements(num, error)
   tra.plotMeasurements()
   tra.plotTraject()
   plt.show()

class DB:
    def __init__(self):
        #10.128.16.12
        #"192.168.0.197"
        #192.168.0.200 
        self.db = MySQLdb.connect(host="10.108.32.18",port=3306,user="auguste",passwd="renasolutions",db="eBike")
        self.cursor         = self.db.cursor()
        self.headerm        = []
        self.headerp        = []
        self.measurements   = []
        self.tindex         = None
        self.latindex       = None
        self.lngindex       = None
        self.altindex       = None
        self.posaccindex    = None
        self.altaccindex    = None
        self.vindex         = None
        self.hindex         = None
        self.bcindex        = None
        self.bvindex        = None
        self.wvindex        = None
        self.whindex        = None
        self.ciindex        = None
        self.weight         = 75

    def getWeight(cls, ID):
        tablename = 'user_settings'
        cls.cursor.execute("SELECT weight FROM "+str(tablename)+" WHERE ID="+str(ID))
        cls.weight = cls.cursor.fetchall()[0][0]
        #print(cls.weight)
        return cls.weight

    def getHeaderM(cls):
        '''get header of measurement table'''
        cls.headerm = []
        tablename = 'measurements'
        cls.cursor.execute("SHOW COLUMNS FROM "+str(tablename))
        headerm = cls.cursor.fetchall()
        for x in headerm:
            cls.headerm.append(x[0])
        cls.tindex      = cls.headerm.index('timestamp')
        cls.latindex    = cls.headerm.index('gps_lat')
        cls.lngindex    = cls.headerm.index('gps_lng')
        cls.altindex    = cls.headerm.index('gps_alt')
        cls.posaccindex = cls.headerm.index('gps_pos_acc')
        cls.altaccindex = cls.headerm.index('gps_alt_acc')
        cls.vindex      = cls.headerm.index('gps_speed')
        cls.hindex      = cls.headerm.index('gps_heading')
        cls.bcindex     = cls.headerm.index('battery_current')
        cls.bvindex     = cls.headerm.index('battery_voltage')
        cls.wvindex     = cls.headerm.index('wind_speed')
        cls.whindex     = cls.headerm.index('wind_heading')
        cls.ciindex     = cls.headerm.index('clearness_index')
        return cls.headerm

    def getHeaderP(cls):
        '''get header of predictions table'''
        cls.headerp = []
        tablename = 'predictions'
        cls.cursor.execute("SHOW COLUMNS FROM "+str(tablename))
        headerp = cls.cursor.fetchall()
        for x in headerp:
            cls.headerp.append(x[0])
        cls.latindexp       = cls.headerp.index('latitude')
        cls.lngindexp       = cls.headerp.index('longitude')
        cls.headingindex    = cls.headerp.index('heading')
        cls.heightindex     = cls.headerp.index('height')
        cls.slopeindex      = cls.headerp.index('slope')
        return cls.headerp


    def getMeasurements(cls, ID=None, traject_ID=None, traject_range = None):
        if (ID):
            cls.getWeight(ID)
        if (ID == None and traject_ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM measurements")
        elif (traject_ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM measurements WHERE ID LIKE '"+str(ID)+"'")
        elif (ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM measurements WHERE traject_ID LIKE '"+str(traject_ID)+"'")
        elif (traject_range != None and ID != None):
            cls.cursor.execute("SELECT * FROM measurements WHERE traject_ID > '"+str(traject_range[0])+"' AND traject_ID < '"+str(traject_range[1])+"' AND ID LIKE '"+str(ID)+"'")
        elif (traject_range == None and traject_ID == None):
            cls.cursor.execute("SELECT * FROM measurements WHERE ID LIKE '"+str(ID)+"'")
        else:
            cls.cursor.execute("SELECT * FROM measurements WHERE traject_ID LIKE '"+str(traject_ID)+"' AND ID LIKE '"+str(ID)+"'")
        measurements = cls.cursor.fetchall()
        for x in measurements:
            cls.measurements.append(Measurement(x[cls.tindex], x[cls.latindex], x[cls.lngindex], x[cls.altindex], x[cls.posaccindex], x[cls.altaccindex], x[cls.vindex], x[cls.hindex], x[cls.bcindex], x[cls.bvindex], x[cls.wvindex], x[cls.whindex], x[cls.ciindex], cls.weight))
        return cls.measurements

    def getTraject(cls, ID=None, traject_ID=None, traject_range=None):
        if (ID):
            cls.getWeight(ID)
        if (ID == None and traject_ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM predictions")
        elif (traject_ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM predictions WHERE ID LIKE '"+str(ID)+"'")
        elif (ID == None and traject_range == None):
            cls.cursor.execute("SELECT * FROM predictions WHERE traject_ID LIKE '"+str(traject_ID)+"'")
            cls.cursor.execute("SELECT * FROM predictions WHERE ID LIKE '"+str(ID)+"'")
        elif (traject_range != None and ID != None):
            cls.cursor.execute("SELECT * FROM predictions WHERE traject_ID > '"+str(traject_range[0])+"' AND traject_ID < '"+str(traject_range[1])+"' AND ID LIKE '"+str(ID)+"'")
        elif (traject_range == None and traject_ID == None):
            cls.cursor.execute("SELECT * FROM predictions WHERE ID LIKE '"+str(ID)+"'")
        else:
            cls.cursor.execute("SELECT * FROM predictions WHERE traject_ID LIKE '"+str(traject_ID)+"' AND ID LIKE '"+str(ID)+"'")
        db_out = cls.cursor.fetchall()
        predictions = []
        for x in db_out:
            dict = {}
            for (key, value) in zip(cls.headerp[3:], x[3:]):
                dict[key] = value
            predictions.append(dict)
        return predictions

    def plot(cls, name):
        if name in cls.headerm:
            cursor.execute("SELECT "+str(name)+" FROM measurements")
            res = cursor.fetchall()
            plt.plot(res)
            return 1
        return -1

def main():
    #newride start tID 34 -- 48 -- 53
    import imp
    imp.reload(cc)
    ID = 31
    tID = None
    db1 = DB() 
    db1.getWeight(ID)
    header = db1.getHeaderM()
    measurements = db1.getMeasurements(ID, traject_ID = 1)#, traject_range = [47, 100])
    headerP = db1.getHeaderP()
    predictions = db1.getTraject(ID, traject_ID = 1)#,traject_range = [47, 100])
    tra = Traject(predictions)
    tra.addMeasurements(measurements)
    #tra.plotTraject()
    #tra.plotMeasurements()
    #tra.plotTrajectOnMap()
    #tra.plotMeasurementsOnMap()
    #tra.plot_power()
    #tra.plot_vc()
    #plt.show()

    segments = cc.getData(tra)
    print(len(segments))
    x0 = [0.6,0.004,2.2]
    sigma = 1 # if this is very small, strong fitting <-> weaker priors. Very large weaker fitting <-> stronger priors
    #res = scipy.optimize.fmin(cc.errorf, x0, args=(segments, sigma))
    res = scipy.optimize.minimize(cc.errorf,x0,args=(segments,sigma), method = 'Nelder-Mead')
    print("optimal parameters, loss function = {:.6e} ".format(cc.errorf(res.x,segments,sigma)))
    print("succes : {:}".format(res.success))
    print("------------------- ")
    print("| CdA  : {:.3f}     ".format(res.x[0]))
    print("| Cr   : {:.3f}     ".format(res.x[1]))
    print("| Pcyc : {:.3f}     ".format(res.x[2]))
    
    pm_guessf    = np.concatenate(cc.estimatePower(res.x,segments))
    pm_measuredf = np.concatenate([ s[2] for s in segments ])
    fig =pl.figure()
    fig.subplots_adjust(left=0.16)
    ax = fig.add_subplot(111)
    #ax.plot([y.speed for x in tra.segments for y in x.measurements],lw=3,ls="dashed",label="speed")
    ax.plot(pm_guessf,marker='s',color="firebrick",lw=3,ls="dashed",label="fit")
    ax.plot(pm_measuredf,marker='o',color="black",lw=3,ls="solid",label="measured")
    ax.legend(frameon=False,fontsize=20)
    ax.set_ylabel("Power (W)",fontsize=20)
    plt.show()

if __name__=="__main__":
    main()
    
