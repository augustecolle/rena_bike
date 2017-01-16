import googlemaps
import pprint as pp
import pandas as pd
import matplotlib.pyplot as plt

samples = 200
startPoint = "brugge, belgium"
endPoint = "gent, belgium"

gmaps = googlemaps.Client(key="AIzaSyAWUyZr-YD30e0gDhqrJqML9VriCurSsJA")
#Get directions and get the polyline
directionResult = gmaps.directions(startPoint, endPoint)
print directionResult
encLine = str(directionResult[0]["overview_polyline"]["points"])
#Get elevation points
elevationResult = gmaps.elevation_along_path(path=encLine, samples=samples)
#Push the result into a dataframe
data = pd.DataFrame(columns=["resolution","elevation", "lat", "lng"])
for point in elevationResult:	
	temp = pd.DataFrame({"resolution": [point["resolution"]], "elevation": [point["elevation"]], "lat":[point["location"]["lat"]], "lng":[point["location"]["lng"]]})
	data = data.append(temp, ignore_index=True)	

print data

fig = plt.figure()
plt.plot(data["elevation"])
plt.show()
