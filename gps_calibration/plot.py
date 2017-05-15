import matplotlib.pyplot as plt
import numpy as np
import csv
import geopy
from subprocess import call

call("mv ~/Downloads/measured.csv ./", shell=True)

lats, longs, accs, speeds = [],[],[],[]
with open("measured.csv", 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        row = [float(x) for x in row[0].split(' ')]
        print(row)
        lats.append(row[0])
        longs.append(row[1])
        accs.append(row[2])
        speeds.append(row[3])


#call("mv ~/Downloads/measured.csv ./", shell=True)
#
#lats, longs = [],[]
#with open("output.csv", 'rb') as csvfile:
#    csvreader = csv.reader(csvfile, delimiter=',')
#    for row in csvreader:
#        row = [float(x) for x in row[0].split(' ')]
#        print(row)
#        lats.append(row[0])
#        longs.append(row[1])


#############################################################

#normalize accuracy to scale scatter label sizes
accs = np.array(accs)/np.sum(accs)
scalar = 1000000

plt.scatter(longs, lats, s=accs*scalar)
plt.show()

import gmplot

gmap = gmplot.GoogleMapPlotter(51.06, 3.71, 16)

#gmap.plot(lats, longs, 'cornflowerblue', edge_width=10)
gmap.scatter(lats, longs, '#3B0B39', size=1, marker=False)
#gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
gmap.heatmap(lats, longs)

gmap.draw("mymap.html")

print("DONE")

#import matplotlib.pyplot as plt
#import numpy as np
#
#plt.scatter(range(len(speeds)), np.array(speeds)*3.6)
#plt.show()
##############################################################
##from www.latlong.net
#true_loc = (51.060766, 3.707900)
#
#error_lat = [x-true_loc[0] for x in lats]
#RMS_error_lat = np.sqrt(np.mean([(x-true_loc[0])**2 for x in lats])/len(lats))
#RMS_error_lat
#
#error_lng = [x-true_loc[1] for x in longs]
#RMS_error_lng = np.sqrt(np.mean([(x-true_loc[1])**2 for x in longs])/len(longs))
#RMS_error_lng
#
##plt.scatter(error_lat, error_lng)
#plt.hist(error_lat, bins=10)
#plt.hist(error_lng, bins=45)
#plt.show()
#
##############################################################
#
#for x in range(len(lats)-1):
#    print(x)
#    geopy.distance.vincenty((lats[x], longs[x]), (lats[x+1], longs[x+1])).meters 
#
#from geopy.distance import vincenty
#
#dist = [geopy.distance.vincenty((lats[x], longs[x]), (lats[x+1], longs[x+1])).meters for x in range(len(lats)-1)]
#
#print(len(dist))
#print(len(accs))
#plt.scatter(lats, longs)
#plt.show()
#
###############################################################
#
