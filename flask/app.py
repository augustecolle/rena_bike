from flask import Flask, request
from flask_restful import Resource, Api
import ssl
import json
import numpy as np
import re
import mechanize
import socket
import numpy as np
from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('logfile.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def i2c(address):
    address = 0x6e
    i2c_helper = ABEHelpers()
    bus = i2c_helper.get_smbus()
    adc = ADCPi(bus, address, rate=18)
    return bus, adc

def getAI(address, channel = 1):
    bus, adc = i2c(address)
    return adc.read_voltage(channel)

def setPGA(address, gain):
    bus, adc = i2c(address)
    adc.set_pga(gain)

import send_email

app = Flask(__name__)
api = Api(app)

global houres
houres = None
global dist_to_end
dist_to_end = None

position = []

class Position(Resource):

    def __init__(self):
        import MySQLdb
        import os
        import urllib2
        import ssl
        import json
        import socket
        #import re
        #import serial
        exists = os.path.isfile("data.db")
        self.db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
        self.cursor = self.db.cursor()
        if not exists:
            print("no database: code one")
            #self.cursor.execute("CREATE TABLE profiles (name text, frictionCoef text, dragCoef text, velocityAv real)")

        #for self signed certificate problems evasion see http://stackoverflow.com/questions/19268548/python-ignore-certicate-validation-urllib2
        global ip
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        temp = urllib2.urlopen("https://"+ip+":5000/Weather", context=ctx)
        temp = temp.readlines()
        temp = json.loads(temp[0])
        self.sky = temp['plotdata'][0]['data']
        self.windspeed = temp['plotdata'][3]['data']
        self.winddir = temp['plotdata'][2]['data']
        self.times = temp['time']
        self.lng = 0
        self.lat = 0
        self.acc = 0
        self.data_raw = 0

        #self.ser=serial.Serial(
        #    port='/dev/serial0',
        #    baudrate=9600,
        #    parity=serial.PARITY_NONE,
        #    stopbits=serial.STOPBITS_ONE,
        #    bytesize=serial.EIGHTBITS,
        #    timeout=1
        #)

    def post(self):
        import time as tm
        try:
            bat_current = getAI(0x6e, 2)
            bat_voltage = getAI(0x6e, 1)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            #By calling logger methods with exc_info=True parameter, traceback is dumped to the logger
            logger.error('Failed to get battery current and/or battery voltage', exc_info=True)

        #cycle analyst, logic level converter needs to be installed
        #x=self.ser.readline()
        #print("raw x")
        #print(x)
        #x = [float(i) for i in re.findall(r"[-+]?\d*\.\d+|\d+", x)]
        #if (len(x) == 13):
        #    print(x)
        #    self.ser.flushInput()
        #    self.ser.flushOutput()

        #update the weather
        try:
            #idx is an index to get the weather at the specified hour
            now = np.round(tm.time())
            idx = np.searchsorted(self.times, now, side="left")
            if idx > 0 and (idx == len(self.times) or math.fabs(now - self.times[idx-1]) < math.fabs(now - self.times[idx])):
                idx = idx-1
            else:
                idx = idx
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Position: Failed to set the index (idx) for the weather', exc_info=True)

        #get ID from database
        try:
            self.cursor.execute("SELECT last_user_ID FROM eBike.global_settings")
            a = self.cursor.fetchall()
            ID = int(a[0][0])
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Position: Failed to get the ID from the database', exc_info=True)

        #set the values to -1 for every key that doesn't come with a value
        try:
            self.data_raw = request.get_json(force=True)
            for (key, value) in self.data_raw.iteritems():
                if (value == None):
                    self.data_raw[key] = -1
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Position: Failed to assign -1 to a key with no value', exc_info=True)

        #Update the database
        try:
            self.cursor.execute("SELECT MAX(traject_ID) FROM eBike.user_settings WHERE ID = "+str(ID)+";")
            a = self.cursor.fetchall()
            traject_ID = a[0][0]
            self.cursor.execute("INSERT INTO eBike.measurements (`ID`, `traject_ID`, `timestamp`, `gps_lat`, `gps_lng`, `gps_alt`, `gps_pos_acc`, `gps_alt_acc`, `gps_speed`, `gps_heading`, `battery_current`, `battery_voltage`, `wind_speed`, `wind_heading`, `clearness_index`) VALUES ("+str(ID)+", "+str(traject_ID)+", "+str(self.data_raw['gps_timestamp'])+", "+str(self.data_raw['gps_lat'])+" ,"+str(self.data_raw['gps_lng'])+" ,"+str(self.data_raw['gps_alt'])+" ,"+str(self.data_raw['gps_pos_acc'])+" ,"+str(self.data_raw['gps_alt_acc'])+" ,"+str(self.data_raw['gps_speed'])+" ,"+str(self.data_raw['gps_heading'])+", "+str(bat_current)+", "+str(bat_voltage)+", "+str(self.windspeed[idx]/3.6)+", "+str(self.winddir[idx])+", "+str(self.sky[idx])+");")
            self.db.commit()
            global position
            position = [self.data_raw['gps_lat'], self.data_raw['gps_lng']]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Position: Failed to update database measurements', exc_info=True)
        return 201

    def get(self):
        global dist_to_end
        if (dist_to_end is not None and dist_to_end < 0.001):
            dist_to_end = None
            return 1
        else:
            return 0

class Weather(Resource):
    from libraries import weather as wh
    import numpy as np
    sky = []
    windspeeds = []
    temperatures = []
    winddirs = []
    times = []

    def __init__(self):
        self.owm = self.wh.owm
        self.lat = None
        self.long = None
        self.raw_data = None
        self.directions = []
        self.houres = {}

    def get(self):
        
        #return [sky[idx], windspeeds[x], winddirs[idx]]
        #print(self.times)
        #print("self.times")
        temp = {'plotdata':[
                {
                'name':'sky',
                'data':self.sky
                },
                {
                'name':'temperature',
                'data':self.temperatures
                },
                {
                'name':'wind direction',
                'data':self.winddirs
                },
                {
                'name':'wind speed',
                'data':self.windspeeds
                }],
                'time':self.times
                }
        return temp

    def post(self):
        try:
            Weather.sky = []
            Weather.windspeeds = []
            Weather.temperatures = []
            Weather.winddirs = []
            Weather.times = []
            self.data_raw = json.dumps(request.get_json(force=True)).encode('utf8')
            self.data_raw = json.loads(self.data_raw)["hourly_forecast"]
            for obj in self.data_raw:
                self.houres[obj["FCTTIME"]["epoch"]] = {
                        "temp" : float(obj["temp"]["metric"]),
                        "sky"  : float(obj["sky"]),
                        "windspeed" : float(obj["wspd"]["metric"]),
                        "winddir" : float(obj["wdir"]["degrees"])
                        }
                Weather.sky.append(float(obj["sky"]))
                Weather.windspeeds.append(float(obj["wspd"]["metric"]))
                Weather.temperatures.append(float(obj["temp"]["metric"]))
                Weather.winddirs.append(float(obj["wdir"]["degrees"]))
                #print(int(obj["FCTTIME"]["epoch"]))
                Weather.times.append(int(obj["FCTTIME"]["epoch"]))
            global houres
            houres = self.houres
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Weather: failed to update on POST information', exc_info=True)
        return houres


class Trajectory(Resource):
    from libraries import trajectory as tr
    def __init__(self):
        import MySQLdb
        import os
        exists = os.path.isfile("data.db")
        self.db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
        self.cursor = self.db.cursor()
        if not exists:
            print("no database: code one")
            #self.cursor.execute("CREATE TABLE profiles (name text, frictionCoef text, dragCoef text, velocityAv real)")

        self.data_raw = None
        self.steps_raw = None
        self.lats = []
        self.longs = []
        self.cycletimes = []
        self.heading = []
        self.distances = []
        self.bearingsFromMapbox = []

    def get(self):
        pass

    def post(self):
        try:
            self.data_raw = json.dumps(request.get_json(force=True)[0]).encode('utf8')
            self.data_raw = json.loads(self.data_raw)
            #self.data_raw is now a dictionary from route object containing the keys [duration, distance, steps, geometry, summary]
            self.lats = []
            self.longs = []
            self.bearingsFromMapbox = []
            for obj in self.data_raw['steps']:
                #print(str(obj['maneuver']['location']['coordinates'][0]) + "\t" + str(obj['maneuver']['location']['coordinates'][1]))
                self.lats.append(obj['maneuver']['location']['coordinates'][1])
                self.longs.append(obj['maneuver']['location']['coordinates'][0]) 
                self.cycletimes.append(obj['duration'])
                self.bearingsFromMapbox.append(obj['heading'])
            cycletimescum = (np.cumsum(self.cycletimes)).tolist()
            formdata = [{"lat":self.lats[i], "lng":self.longs[i], "cycletimes":self.cycletimes[i], "cycletimescum":cycletimescum[i], "bearingsFromMapbox":self.bearingsFromMapbox[i]} for i in range(len(self.lats))] #for google API
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Trajectory: failed to update on POST information', exc_info=True)
        return formdata, 201

    #def getHeights(self):
    #    formdata = ''.join(str(self.lats[i]) + "\t" + str(self.longs[i]) + "\n" for i in range(len(self.lats)))
    #    br = mechanize.Browser()
    #    br.set_handle_robots(False)
    #    br.addheaders = [('User-agent', 'Firefox')]
    #    # Retrieve the Google home page, saving the response
    #    br.open("http://www.gpsvisualizer.com/convert_input")
    #    #br.open("https://www.google.be")
    #    # Select the search box and search for 'foo'
    #    br.select_form( 'convert_form' )
    #    br.form[ 'data' ] = formdata
    #    control = br.find_control(name="add_elevation", type="select")
    #    #set dropdown menu to auto to include elevation
    #    control.value = ["auto"]
    #    # Get the search results
    #    br.submit()
    #    for i in br.links(text_regex='Click'):
    #        #print(i)
    #        f = br.retrieve(i.absolute_url, filename = './data.txt')
    #    #print("Scraped the heights")

class Energy(Resource):
    def __init__(self):
        from libraries import cyclist as cl
        from libraries import trajectory as tr
        import MySQLdb
        import os
        exists = os.path.isfile("data.db")
        self.db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
        self.cursor = self.db.cursor()
        if not exists:
            print("no database: code one")
            #self.cursor.execute("CREATE TABLE profiles (name text, frictionCoef text, dragCoef text, velocityAv real)")
        self.init = 0
        self.tr = tr.traject()
        self.cl = cl.cyclist()
        global houres
        self.tr.weather = houres
      
    def get(self):
        return json.dumps(self.energies)

    def post(self):
        from scipy import spatial
        import numpy as np
        global position
        #self.data_raw = json.dumps(request.get_json(force=True)[0]).encode('utf8')
        try:
            data_raw = request.get_json(force=True)
            self.tr.heights = data_raw["heights"]
            self.tr.longitudes = data_raw["lngs"]
            self.tr.latitudes = data_raw["lats"]
            newRoute = int(data_raw["newRoute"])
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Energy: failed to parse information from POST', exc_info=True)

        #find nearest knot and only update calculation when following the proposed route
        try:
            dist_to_start = np.linalg.norm(np.array(position) - np.array([self.tr.latitudes[0], self.tr.longitudes[0]]))
            global dist_to_end
            dist_to_end = np.linalg.norm(np.array(position) - np.array([self.tr.latitudes[-1], self.tr.longitudes[-1]]))
            #find the index of the nearest knot
            dist, index = spatial.KDTree([[x,y] for x,y in zip(self.tr.latitudes, self.tr.longitudes)]).query(position)
            # only update if the nearest knot is close enough
            if (dist > 0.002):
                index = 0
            if (index == len(self.tr.heights)-1):
                index = index - 1
            self.tr.heights = data_raw["heights"][index:]
            self.tr.longitudes = data_raw["lngs"][index:]
            self.tr.latitudes = data_raw["lats"][index:]
            self.tr.bearingsFromMapbox = data_raw["bearingsFromMapbox"][index:]
            self.tr.cycletimes = data_raw["cycletimes"][index:]
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Energy: failed to try get the nearest knot', exc_info=True)
 
        self.tr.cycletimescum = (np.cumsum(self.tr.cycletimes)).tolist()
        self.tr.get_distances()
        self.tr.get_compass_bearing()
        self.tr.get_slopes()
        self.cursor.execute("SELECT last_user_ID FROM eBike.global_settings")
        a = self.cursor.fetchall()
        ID = int(a[0][0])
        try:
            self.cursor.execute("SELECT gps_speed FROM measurements WHERE ID = "+str(ID)+";")
            res = self.cursor.fetchall()
            res = [v[0] for v in res if v[0] > 0]
            #select cyclist average velocity if this can be defined, otherwise get from database.
            if (index == 0 and len(res) > 60*60):
                v_cyclist = np.mean(res)
            elif (len(res) > 60*5 and index is not 0): #mean of last 5 minutes cycling
                v_cyclist = np.mean(res)
            else:
                self.cursor.execute("SELECT v_cyclist FROM user_settings WHERE ID = "+str(ID)+";")
                v_cyclist = int(self.cursor.fetchall()[0][0])
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Energy: failed to calculate average speed', exc_info=True)
            
        try: 
            self.energies = self.cl.cycle_traject_cv(trajectory = self.tr, cv=v_cyclist)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Energy: failed to cycle the traject and get energies', exc_info=True)

        try:
            if (newRoute == 1): #only store data on initial routing
                #self.init = 1
                self.cursor.execute("SELECT last_user_ID FROM eBike.global_settings")
                a = self.cursor.fetchall()
                ID = int(a[0][0])
                self.cursor.execute("SELECT MAX(traject_ID) FROM eBike.user_settings WHERE ID = "+str(ID)+";")
                a = self.cursor.fetchall()
                #only new traject_ID when routing, not when updating
                if (newRoute == 1):
                    traject_ID = int(a[0][0]) + 1
                else:
                    traject_ID = int(a[0][0])
                self.cursor.execute("UPDATE eBike.user_settings SET traject_ID = "+str(traject_ID)+" WHERE ID = "+str(ID)+";")
                self.db.commit()
                temp = self.tr.avg_slopes
                temp.append(0)
                for lat, lng, heading, height, slope in zip(self.tr.latitudes, self.tr.longitudes, self.tr.bearingsFromMapbox, self.tr.heights, temp):
                    self.cursor.execute("INSERT INTO eBike.predictions (`ID`, `traject_ID`, `latitude`, `longitude`, `heading`, `height`, `slope`) VALUES ("+str(ID)+", "+str(traject_ID)+", "+str(lat)+" ,"+str(lng)+", "+str(heading)+", "+str(height)+", "+str(slope)+");")
                self.db.commit()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            logger.error('Energy: failed to update database', exc_info=True)

        return json.dumps(self.energies), 201

class Settings(Resource):

    def __init__(self):
        import MySQLdb
        import os
        exists = os.path.isfile("data.db")
        self.db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
        self.cursor = self.db.cursor()
        self.data = {}
        if not exists:
            print("no database: code one")
            #self.cursor.execute("CREATE TABLE profiles (name text, frictionCoef text, dragCoef text, velocityAv real)")

    def get(self): #Send all profile settings
        self.data = {}
        self.cursor.execute("SELECT * FROM user_settings;")
        data = self.cursor.fetchall()
        self.cursor.execute("SHOW columns FROM user_settings;")
        self.header = [x[0] for x in self.cursor.fetchall()]
        self.data = {str(data[i][0]) : {str(self.header[j]) : data[i][j] for j in range(len(self.header))} for i in range(len(data))}
        return json.dumps(self.data), 201

    def post(self): #Save a new profile
        data_raw = request.get_json(force=True)
        self.cursor.execute("SELECT ID FROM eBike.user_settings")
        a = self.cursor.fetchall()
        if (int(data_raw.values()[0][0]) in [x[0] for x in a]):
            self.cursor.execute("UPDATE eBike.user_settings SET name = '"+str(data_raw.keys()[0])+"', weight = "+str(data_raw.values()[0][1])+", length = "+str(data_raw.values()[0][2])+", cr = "+str(data_raw.values()[0][3])+", cda = "+str(data_raw.values()[0][4])+", v_cyclist = "+str(data_raw.values()[0][5])+" WHERE user_settings.ID = "+str(data_raw.values()[0][0])+";")
            self.db.commit()
            self.cursor.execute("UPDATE eBike.global_settings SET last_user_ID = "+str(data_raw.values()[0][0])+";")
        else:
            self.cursor.execute("INSERT INTO eBike.user_settings (`ID`, `name`, `weight`, `length`, `P_k`, `P_lambda`, `v_k`, `v_lambda`, `cr`, `cda`, `v_cyclist`) VALUES (NULL,'"+str(data_raw.keys()[0])+"',"+str(data_raw.values()[0][1])+" ,"+str(data_raw.values()[0][2])+" , 0, 0, 0, 0, "+str(data_raw.values()[0][3])+", "+str(data_raw.values()[0][4])+", "+str(data_raw.values()[0][5])+");")
            self.db.commit()
            self.cursor.execute("SELECT ID FROM eBike.user_settings")
            a = self.cursor.fetchall()
            self.db.commit()
            self.cursor.execute("UPDATE eBike.global_settings SET last_user_ID = "+str(max(a)[0])+";")

        self.db.commit()
        return 201

    def delete(self): #Delete a profile
        print "delete"


class globalSettings(Resource):
    def __init__(self):
        import MySQLdb
        import os
        exists = os.path.isfile("data.db")
        self.db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
        self.cursor = self.db.cursor()
        self.data = {}
        if not exists:
            print("no database: code one")
            #self.cursor.execute("CREATE TABLE profiles (name text, frictionCoef text, dragCoef text, velocityAv real)")

    def get(self):
        self.cursor.execute("SELECT last_user_ID FROM eBike.global_settings")
        return self.cursor.fetchall()[0][0]

    def post(self):
        data_raw = request.get_json(force=True)
        self.cursor.execute("UPDATE eBike.global_settings SET last_user_ID = "+str(data_raw)+";")
        self.db.commit()
        return 201


api.add_resource(Weather, '/Weather')
api.add_resource(Trajectory, '/Trajectory')
api.add_resource(Energy, '/Energy')
api.add_resource(Settings, '/Settings')
api.add_resource(Position, '/Position')
api.add_resource(globalSettings, '/globalSettings')

#appble CORS (cross origin requests), from: http://coalkids.github.io/flask-cors.html
@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']
        h = resp.headers 
        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers
        return resp

@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers
    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp


if __name__ == "__main__":
    global ip
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1] #str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
    context = ('/etc/apache2/ssl/apache.crt', '/etc/apache2/ssl/apache.key')
    app.run(debug=False, host=ip, ssl_context=context, port=5000, threaded=True)


