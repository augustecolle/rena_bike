from flask import Flask, request
from flask_restful import Resource, Api
import ssl
import json
import numpy as np
import re
import mechanize
import socket

app = Flask(__name__)
api = Api(app)

global houres
houres = None

class Position(Resource):

    def __init__(self):
        self.lng = 0
        self.lat = 0
        self.acc = 0
        self.data_raw = 0

    def post(self):
        print(request.get_json(force=True))
        #self.data_raw = json.dumps(request.get_json(force=True)[0]).encode('utf8')
        #self.data_raw = json.loads(self.data_raw)
        #print(self.data_raw)
        return 201

    def get(self):
        return json.dumps(self.data_raw)



class Weather(Resource):
    from libraries import weather as wh
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
        return houres


class Trajectory(Resource):
    from libraries import trajectory as tr
    def __init__(self):
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
            print("BEARING FROM MAPBOX")
            print(obj['heading'])
            #self.heading.append(obj['heading'])
            #self.distances.append(obj['distance'])
        #formdata = ''.join(str(self.lats[i]) + "," + str(self.longs[i]) + "|" for i in range(len(self.lats)))
        #formdata = formdata[:-1] #remove trailing |
        cycletimescum = (np.cumsum(self.cycletimes)).tolist()
        formdata = [{"lat":self.lats[i], "lng":self.longs[i], "cycletimes":self.cycletimes[i], "cycletimescum":cycletimescum[i], "bearingsFromMapbox":self.bearingsFromMapbox[i]} for i in range(len(self.lats))] #for google API
        #self.getHeights()
        return formdata, 201

    def getHeights(self):
        formdata = ''.join(str(self.lats[i]) + "\t" + str(self.longs[i]) + "\n" for i in range(len(self.lats)))
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Firefox')]
        # Retrieve the Google home page, saving the response
        br.open("http://www.gpsvisualizer.com/convert_input")
        #br.open("https://www.google.be")
        # Select the search box and search for 'foo'
        br.select_form( 'convert_form' )
        br.form[ 'data' ] = formdata
        control = br.find_control(name="add_elevation", type="select")
        #set dropdown menu to auto to include elevation
        control.value = ["auto"]
        # Get the search results
        br.submit()
        for i in br.links(text_regex='Click'):
            #print(i)
            f = br.retrieve(i.absolute_url, filename = './data.txt')
        #print("Scraped the heights")

class Energy(Resource):
    energies = {}
    def __init__(self):
        from libraries import trajectory as tr
        from libraries import cyclist as cl
        self.tr = tr.traject()
        self.cl = cl.cyclist()
        global houres
        self.tr.weather = houres
        
    def get(self):
        return json.dumps(self.energies)

    def post(self):
        #self.data_raw = json.dumps(request.get_json(force=True)[0]).encode('utf8')
        data_raw = request.get_json(force=True)
        #print(data_raw)
        self.tr.heights = data_raw["heights"]
        self.tr.longitudes = data_raw["lngs"]
        self.tr.latitudes = data_raw["lats"]
        self.tr.bearingsFromMapbox = data_raw["bearingsFromMapbox"]
        print("BEARINGS IN ENERGY")
        print(str(self.tr.bearingsFromMapbox))
        self.tr.cycletimes = data_raw["cycletimes"]
        self.tr.cycletimescum = (np.cumsum(self.tr.cycletimes)).tolist()
        self.tr.get_distances()
        self.tr.get_compass_bearing()
        self.tr.get_slopes()
        self.energies = self.cl.cycle_traject_cv(trajectory = self.tr, cv=30)
        #print(self.energies)
        #print(self.data_raw)
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
        print(data_raw)
        self.cursor.execute("SELECT ID FROM eBike.user_settings")
        a = self.cursor.fetchall()
        if (int(data_raw.values()[0][0]) in [x[0] for x in a]):
            self.cursor.execute("UPDATE eBike.user_settings SET name = '"+str(data_raw.keys()[0])+"', weight = "+str(data_raw.values()[0][1])+", length = "+str(data_raw.values()[0][2])+", cr = "+str(data_raw.values()[0][3])+", cda = "+str(data_raw.values()[0][4])+", v_wind = "+str(data_raw.values()[0][5])+", v_cyclist = "+str(data_raw.values()[0][6])+" WHERE user_settings.ID = "+str(data_raw.values()[0][0])+";")
        else:
            self.cursor.execute("INSERT INTO eBike.user_settings (`ID`, `name`, `weight`, `length`, `P_k`, `P_lambda`, `v_k`, `v_lambda`, `cr`, `cda`, `v_wind`, `v_cyclist`) VALUES (NULL,'"+str(data_raw.keys()[0])+"',"+str(data_raw.values()[0][1])+" ,"+str(data_raw.values()[0][2])+" , 0, 0, 0, 0, "+str(data_raw.values()[0][3])+", "+str(data_raw.values()[0][4])+", "+str(data_raw.values()[0][5])+" , "+str(data_raw.values()[0][6])+");")

        self.db.commit()
        self.cursor.execute("UPDATE eBike.global_settings SET last_user_ID = "+str(data_raw.values()[0][0])+";")

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
        print(data_raw)
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
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1] #str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
    context = ('/etc/apache2/ssl/apache.crt', '/etc/apache2/ssl/apache.key')
    app.run(debug=False, host=ip, ssl_context=context, port=5000, threaded=True)


