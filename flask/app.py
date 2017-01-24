from flask import Flask, request
from flask_restful import Resource, Api
import ssl
import pyowm

app = Flask(__name__)
api = Api(app)

class Weather(Resource):
    def __init__(self):
        self.owm = pyowm.OWM('aab29414b85baab539aeac7451de4b45')
        self.lat = None
        self.long = None

    def get(self):
        self.lat = request.args.get('lat')
        self.long = request.args.get('long')
        fc = self.get_detailed_forecast_lat_long(self.lat, self.long)
        return fc


    def get_weather_lat_long(self, latitude, longitude, numstations = 1):
        '''returns the pyown weather object(s) in a list'''
        obs_list = self.owm.weather_around_coords(latitude, longitude, limit = numstations)
        weather_obj_list = []
        for obs in obs_list:
            loc = obs.get_location()
            print(loc)
            weather_obj_list.append(obs.get_weather())
        return weather_obj_list


    def get_winddata_lat_long(self, latitude, longitude, numstations = 1):
        '''Gets wind data for given latitude and longitude. Numstations defaults to 1, if more than 1 station is asked (and if more stations are available) a list of dictionaries will be returned, each containing the weather data from the station.'''
        print(latitude)
        print(longitude)
        weather_list = get_weather_lat_long(float(latitude), float(longitude), numstations)
        list_wind_data = []
        for weather in weather_list:
            list_wind_data.append(weather.get_wind())
        return list_wind_data


    def get_forecast_lat_long(self, latitude, longitude, numdays=None):
        '''returns forecast object given lat, long and numdays'''
        if (numdays == None): numdays = 1
        fc = self.owm.daily_forecast_at_coords(float(latitude), float(longitude), limit = numdays)
        return fc.get_forecast()


    def get_detailed_forecast_lat_long(self, latitude, longitude):
        '''returns detailed 3 hourly forecast in a range of 5 days for given coords'''
        fc = self.owm.three_hours_forecast_at_coords(float(latitude), float(longitude))
        f = fc.get_forecast()
        wStr = ""
        for weather in f:
            wStr = wStr + (weather.get_reference_time('iso') + "\t" + weather.get_detailed_status() + "\n")
        return wStr

api.add_resource(Weather, '/Weather')

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


