import pyowm

owm = pyowm.OWM('aab29414b85baab539aeac7451de4b45')

def get_weather_lat_long(latitude, longitude, numstations = 1):
    '''returns the pyown weather object(s) in a list'''
    obs_list = owm.weather_around_coords(latitude, longitude, limit = numstations)
    weather_obj_list = []
    for obs in obs_list:
        loc = obs.get_location()
        print(loc)
        weather_obj_list.append(obs.get_weather())
    return weather_obj_list


def get_winddata_lat_long(latitude, longitude, numstations = 1):
    '''Gets wind data for given latitude and longitude. Numstations defaults to 1, if more than 1 station is asked (and if more stations are available) a list of dictionaries will be returned, each containing the weather data from the station.'''
    print(latitude)
    print(longitude)
    weather_list = get_weather_lat_long(float(latitude), float(longitude), numstations)
    list_wind_data = []
    for weather in weather_list:
        list_wind_data.append(weather.get_wind())
    return list_wind_data
        

def get_forecast_lat_long(latitude, longitude, numdays=None):
    '''returns forecast object given lat, long and numdays'''
    if (numdays == None): numdays = 1
    fc = owm.daily_forecast_at_coords(float(latitude), float(longitude), limit = numdays)
    return fc.get_forecast()


def get_detailed_forecast_lat_long(latitude, longitude):
    '''returns detailed 3 hourly forecast in a range of 5 days for given coords'''
    fc = owm.three_hours_forecast_at_coords(float(latitude), float(longitude))
    f = fc.get_forecast()
    for weather in f:
        print(weather.get_reference_time('iso') + "\t" + weather.get_detailed_status())
    return f
