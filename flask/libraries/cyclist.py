import trajectory as tr
import weather as wh
import numpy as np

class cyclist(object):
    '''This class contains everything related to the cyclist'''

    coords_of_ghent = [51.0543, 3.7174] #static, defaults for cyclist's locations so outside of init

    def __init__(self, weight = None, length = None, coords = None, name = None, velocity = None, compassbearing = None, wind = None, height = None, slope = None):
        if (weight == None): weight = 80
        if (length == None): length = 1.8
        if (coords == None): coords = self.coords_of_ghent
        if (name == None): name = "default"
        if (compassbearing == None): compassbearing = 0
        if (velocity == None): velocity = 0
        self.weight = weight
        self.length = length
        self.coords = coords
        self.name = name
        self.velocity = velocity
        self.compassbearing = compassbearing
        self.height = height
        self.wind = wind
        self.slope = slope

    def get_weight(self):
        return self.weight
    
    def get_length(self):
        return self.length

    def get_position(self):
        '''returns position of cyclist in coords'''
        return self.coords

    def get_name(self):
        return self.name

    def set_weight(self, weight):
        '''weight of the cyclist in kg'''
        self.weight = weight
        return self.weight

    def set_length(self, length):
        '''length of the cyclist in meter'''
        self.length = length
        return self.length

    def set_position(self, latitude, longitude):
        '''set coords of cyclist'''
        self.coords[0] = latitude
        self.coords[1] = longitude

    def set_name(self, name):
        self.name = name
        return self.name

    def get_CdA(self):
        '''TO DO: CALCULATE CdA for different angles from solidworks model'''
        return 0.6 #6.24*0.3048**2 #0.6

    def get_Pwind(self, i, trajectory):
        if (self.wind == None):
            print("WIND ERROR")
            #start = self.coords
            #self.wind = wh.get_winddata_lat_long(start[0], start[1])
            #print(self.wind)
            #get windspeed
        orderedHoures = trajectory.weather.keys()
        orderedHoures.sort()
        index = int(trajectory.cycletimescum[i]/3600.0)
        print(index)
        v_wind = float(trajectory.weather[orderedHoures[index]]['windspeed']) #already in m/s
        print("VWIND: ")
        print(str(v_wind))
        #head_wind_alpha = self.compassbearing - (trajectory.weather[orderedHoures[index]]['winddir'])
        print("BEARINGS: ")
        print(str(trajectory.weather[orderedHoures[index]]['winddir']) + "\t" + str(trajectory.bearingsFromMapbox[i]))
        head_wind_alpha = trajectory.bearingsFromMapbox[i] - (trajectory.weather[orderedHoures[index]]['winddir'])
        print("HEAD WIND")
        print(str(head_wind_alpha))
        print("BEARING")
        #head_wind_alpha = self.compassbearing - 90
        #------REMOVE THIS------#
        head_wind_alpha = 180
        v_wind = 20/3.6
        ########################
        CdA = self.get_CdA() 
        rho = tr.get_air_density_at_height(self.height)
        P_wind = 0.5*rho*CdA*self.velocity*\
                (self.velocity**2 + v_wind**2 - 2*self.velocity*v_wind*np.cos(head_wind_alpha*np.pi/180))\
                *np.cos(np.arctan(v_wind*np.sin(head_wind_alpha*np.pi/180)/(self.velocity + (v_wind*np.cos(head_wind_alpha*np.pi/180))))) #From the thesis of Guylian Stevens
        return P_wind

    def get_Prol(self, Crol = None):
        #TO DO: implement bicycle class and get bicycle parameters from there
        if (Crol == None):
            Crol = 0.004 #bicycle tire on asphalt, engineeringtoolbox.com
        Prol = self.weight*9.807*self.velocity*Crol
        return Prol

    def get_Pklim(self):
        Pklim = np.sin(np.arctan(self.slope))*self.weight*9.807*self.velocity
        return Pklim

    def cycle_traject_cv(self, trajectory = None, cv = None):
        '''cycle given trajectory at constant velocity (cv), cv defaults to 20 km/h'''
        if (trajectory == None):
            print("No trajetory given, exiting method ...")
            return -1
        if (cv == None): cv = 20/3.6
        self.velocity = cv/3.6
        P_wind = np.array([])
        E_wind = np.array([])
        P_rol = np.array([])
        E_rol = np.array([])
        P_klim = np.array([])
        E_klim = np.array([])
        start = trajectory.get_startPosition()
        mid = [trajectory.latitudes[len(trajectory.distances)/2], trajectory.longitudes[len(trajectory.distances)/2]]
        self.coords = start
        #self.wind = wh.get_winddata_lat_long(mid[0], mid[1])
        self.wind = trajectory.weather 
        #print(self.wind)
        compassbearings = np.array(trajectory.get_compass_bearing())
        #print(head_wind)
        distances = trajectory.distances
        slopes = trajectory.get_slopes()
        #each 500 meters full stop and again accelarating
        #E_acc = 0.5*self.weight*self.velocity**2*(np.round(np.sum(trajectory.distances)/500.0))/3600.0*1/(len(trajectory.distances)) #in Wh
        fmt = '%-8s%-20s%-20s%s'
        #print(fmt % ('', 'Distances', 'Compassbearing', 'Winddirection'))
        for i in range(len(distances)):
            self.compassbearing = compassbearings[i]
            self.height = trajectory.heights[i]
            self.slope = slopes[i]
            #print(fmt % (i, distances[i], compassbearings[i], self.wind[0]['deg']))
            P_wind = np.append(P_wind, self.get_Pwind(i, trajectory)) 
            E_wind = np.append(E_wind, self.get_Pwind(i, trajectory)*distances[i]/self.velocity*1.0/3600) #in Wh
            P_rol = np.append(P_rol, self.get_Prol()) 
            E_rol = np.append(E_rol, self.get_Prol()*distances[i]/self.velocity*1.0/3600) 
            P_klim = np.append(P_klim, self.get_Pklim()) 
            E_klim = np.append(E_klim, self.get_Pklim()*distances[i]/self.velocity*1.0/3600) 
        return {'position' : (np.cumsum(distances)/1000.0).tolist(),
                'power' : [
                    {'name' : 'Pwind', 'data' : P_wind.tolist()},
                    {'name' : 'Prol' , 'data' : P_rol.tolist()},
                    {'name' : 'Pklim', 'data' : [x if x >= 0  else 0 for x in P_klim.tolist()]},
                    {'name' : 'Ptot', 'data' : (P_wind + P_rol + P_klim).tolist()}
                    ],
                'energy': [
                    {'name' : 'Ewind', 'data' : (np.cumsum(E_wind)).tolist()},
                    {'name' : 'Erol' , 'data' : (np.cumsum(E_rol)).tolist()},
                    {'name' : 'Eklim', 'data' : (np.cumsum([x if x >= 0 else 0 for x in E_klim])).tolist()},
                    #{'name' : 'Eacc' , 'data' : (np.cumsum(E_acc)).tolist()},
                    {'name' : 'Etot' , 'data' : (np.cumsum(E_wind) + np.cumsum(E_rol) + np.cumsum([x if x >= 0 else 0 for x in E_klim])).tolist()}],
                'altitude' : trajectory.heights}


