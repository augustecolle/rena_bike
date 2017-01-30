from flask import Flask, request
from flask_restful import Resource, Api
import ssl
import pyowm

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
        pass 
    def get(self):
        pass
    def post(self):
        print(request.form)
        print(request.files)
        print(request.get_json(force=True))
        return 0, 201

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


