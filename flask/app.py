from flask import Flask, request
from flask_restful import Resource, Api
import ssl
import pyowm
import json
import re
import mechanize


app = Flask(__name__)
api = Api(app)

class Weather(Resource):
    from libraries import weather as wh
    def __init__(self):
        self.owm = self.wh.owm
        self.lat = None
        self.long = None

    def get(self):
        print(request.args)
        self.lat = request.args.get('lat')
        self.long = request.args.get('long')
        fc = self.wh.get_detailed_forecast_lat_long(self.lat, self.long)
        print fc
        return fc

class Trajectory(Resource):
    from libraries import trajectory as tr
    def __init__(self):
        self.data_raw = None
        self.steps_raw = None
        self.lats = []
        self.longs = []
    def get(self):
        pass
    def post(self):
        self.data_raw = json.dumps(request.get_json(force=True)[0]).encode('utf8')
        self.data_raw = json.loads(self.data_raw)
        #self.data_raw is now a dictionary from route object containing the keys [duration, distance, steps, geometry, summary]
        self.lats = []
        self.longs = []
        for obj in self.data_raw['steps']:
            print(str(obj['maneuver']['location']['coordinates'][0]) + "\t" + str(obj['maneuver']['location']['coordinates'][1]))
            self.lats.append(obj['maneuver']['location']['coordinates'][1])
            self.longs.append(obj['maneuver']['location']['coordinates'][0]) 
        formdata = ''.join(str(self.lats[i]) + "\t" + str(self.longs[i]) + "\n" for i in range(len(self.lats)))
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
            print(i)
            f = br.retrieve(i.absolute_url, filename = './data.txt')
        print("Scraped the heights")


api.add_resource(Weather, '/Weather')
api.add_resource(Trajectory, '/Trajectory')

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
    context = ('/etc/apache2/ssl/apache.crt', '/etc/apache2/ssl/apache.key')
    app.run(debug=False, host="0.0.0.0", ssl_context=context, port=5000, threaded=True)


