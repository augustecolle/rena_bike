import MySQLdb
import csv


db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
cursor = db.cursor()

cursor.execute("SELECT * FROM eBike.predictions WHERE traject_ID = 26;")
a = cursor.fetchall()
#lats = [x[4] for x in a]
#longs = [x[5] for x in a]
#accuracies = [x[7] for x in a]
#speeds = [x[9] for x in a]

lats = [x[3] for x in a]
longs = [x[4] for x in a]


with open('measured.csv', 'wb') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=' ')
    for lat,lng,acc,speed in zip(lats, longs, accuracies, speeds):
        csv_writer.writerow([lat,lng,acc,speed])


#cursor.execute("SELECT * FROM eBike.predictions;")
#a = cursor.fetchall()
#lats = [x[3] for x in a]
#longs = [x[4] for x in a]
#
#with open('predicted.csv', 'wb') as csvfile:
#    csv_writer = csv.writer(csvfile, delimiter=' ')
#    for lat,lng in zip(lats, longs):
#        csv_writer.writerow([lat,lng])
#



