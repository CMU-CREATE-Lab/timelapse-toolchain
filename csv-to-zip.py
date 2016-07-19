# CMU CREATE Lab
# Python 2.7

import os, array, csv, json, math, random, urllib2, sys
from datetime import datetime
import zipfile

def LonLatToPixelXY(lonlat):
    (lon, lat) = lonlat
    x = (lon + 180.0) * 256.0 / 360.0
    y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
    return [x, y]

def YearMonthDayToEpoch(year, month, day):
  return (datetime(int(year), int(month), int(day)) - datetime(1970, 1, 1)).total_seconds()

def LonLatToECEF(lon,lat, elv = 0):
    lat = lat * (math.pi/180)
    lon = lon * (math.pi/180)
    radius = (6.371e6 + elv) / 6.371e6
    x = -radius * math.cos(lat) * math.sin(lon)
    y = radius * math.sin(lat)
    z = -radius * math.cos(lat)*math.cos(lon)
    return [x,y,z]


def main(file):
	print 'processing ' + file
	
def process(file):
	print 'main routine'

	rows = []
	with open("capture/or/OG_Permits_02-10-2016.csv") as f:
	        reader = csv.DictReader(f)
	        for row in reader:
	            rows.append(row)

	data = []
	for row in rows:
	    if row['Status'] == 'Cancelled':
	        continue
	    try:
	        date = datetime.strptime(row['ApplicationDate'], '%d-%b-%y')
	        if date > datetime(1800, 1, 1) and date < datetime.now() - relativedelta(years=100):
	            date = date + relativedelta(years=100)
	    except ValueError:
	        print 'error converting date for: ', row
	        continue
	    try:
	        lon = float(row['Longitude'])
	        lat = float(row['Latitude'])
	    except ValueError:
	        print 'error converting coordinate for: ', row
	        continue
	    x,y = LonLatToPixelXY([lon,lat])
	    epochtime = (date - datetime(1970, 1, 1)).total_seconds()
	    data += [x,y,epochtime]

	f.close()
	array.array('f', data).tofile(open('data/or.bin', 'wb'))


if __name__ == "__main__":
	if len(sys.argv) != 1 or sys.argv[1][-3:] != 'csv':
		print 'invalid arguments. Please provide valid path to csv file. e.g. "python csv-to-zip.py /Users/megge/data.csv"'
	main(sys.argv[1])