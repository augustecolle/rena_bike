import MySQLdb
import csv


db = MySQLdb.connect("localhost", "python_user", "test", "eBike")
cursor = db.cursor()

cursor.execute("SELECT * FROM eBike.measurements;")
a = cursor.fetchall()
lats = [x[3] for x in a]
longs = [x[2] for x in a]
accuracies = [x[5] for x in a]


with open('output.csv', 'wb') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=' ')
    for lat,lng,acc in zip(lats, longs, accuracies):
        csv_writer.writerow([lat,lng,acc])



