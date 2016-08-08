# CMU CREATE Lab
# Python 2.7

import os, array, csv, json, math, random, urllib2, sys, string
from datetime import datetime
from dateutil.parser import parse
import zipfile

# some useful constants	
second = 1000
minute = 60 * second
hour = 60 * minute
day = 24 * hour
year = 365 * day



def LonLatToPixelXY(lonlat):
	(lon, lat) = lonlat
	x = (lon + 180.0) * 256.0 / 360.0
	y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
	return [x, y]

def YearMonthDayToEpoch(year, month, day):
  return (datetime(int(year), int(month), int(day)) - datetime(1970, 1, 1)).total_seconds()
	
def generate_lat_lon_time_binary(data):
	# to do: implement handling of CSVs without headers
	rows = []
	with open(data['file']) as f:
		reader = csv.DictReader(f)
		for row in reader:
			rows.append(row)

	for row in rows:
		row.update(dict((k.lower(), v) for k,v in row.iteritems())) # convert keys to lower case

	col_names = rows[0].keys()
	
	lat_col = [i for i in ['lat', 'latitude', 'y'] if i in col_names][0]
	lon_col = [i for i in ['lon', 'long', 'longitude', 'x'] if i in col_names][0]
	date_col = [i for i in ['date', 'time', 'datetime', 'dates', 'times', 't'] if i in col_names][0]

	item_count = len(rows)
	
	items = []

	for row in rows:
		try:
			date = parse(row[date_col], ignoretz=True)
		except ValueError:
			print 'error converting date for: ', row
			continue
		try:
			lon = float(row[lon_col])
			lat = float(row[lat_col])
		except ValueError:
			print 'error converting coordinate for: ', row
			continue
		
		if lon > data['max_x']:
			data['max_x'] = lon
		elif lon < data['min_x']:
			data['min_x'] = lon
		if lat > data['max_y']:
			data['max_y'] = lat
		elif lat < data['min_y']:
			data['min_y'] = lat

		if date < data['start_time']:
			data['start_time'] = date
		if date > data['end_time']:
			data['end_time'] = date

		x,y = LonLatToPixelXY([lon,lat])
		epochtime = (date - datetime(1970, 1, 1)).total_seconds() * 1000 # // time in JavaScript epoch time (milliseconds since 1970) in UTC timezone
		items += [x,y,epochtime]

	data['bin_url'] = data['base_name'] + '.bin'
	array.array('f', items).tofile(open(data['bin_url'], 'wb'))

	return data

def calc_span_increment(data):
	span = (data['end_time'] - data['start_time']).total_seconds() * 1000

	if span <= second:
		increment = 1
	elif span <= minute:
		increment = 200
	elif span <= hour:
		increment = 10 * second
	elif span <= day:
		increment = 5 * minute
	elif span <= 7 * day:
		increment = 30 * minute
	elif span <= 30 * day:
		increment = 2 * hour
	elif span <= 180 * day:
		increment = 6 * hour
	elif span <= 365 * day:
		increment = day
	elif span <= 15 * year:
		increment = (span // year) * day
	elif span <= 50 * year:
		increment = 30 * day
	elif span <= 500 * year:
		increment = year
	elif span <= 15000:
		increment = 10 * year
	else:
		increment = year

	#data['increment'] = increment
	#data['span'] = span	

	return (span, increment)

def calc_centroid_zoom(data):
	# sets default zoom level for 800 x 600
	lat1 = math.radians(data['min_y'])
	lon1 = math.radians(data['min_x'])
	lat2 = math.radians(data['max_y'])
	lon2 = math.radians(data['max_x'])
	dLng = math.radians(data['min_x'] - data['max_x'])

	Bx = math.cos(lat2) * math.cos(dLng)
	By = math.cos(lat2) * math.sin(dLng)
	lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), \
	        math.sqrt( (math.cos(lat1) + Bx) * (math.cos(lat1) + Bx) + By * By) )
	lon3 = lon1 + math.atan2(By, math.cos(lat1) + Bx)

	mid_y = round(math.degrees(lat3), 4)
	mid_x = round(math.degrees(lon3), 4)

	latFraction = (lat2 - lat1) / math.pi
	lngDiff = data['max_x'] - data['min_x']
	if lngDiff < 0:
	    lngDiff += 360
	lngFraction = lngDiff / 360
	latZoom = math.floor(math.log(768 / 256 / latFraction) / math.log(2))
	lngZoom = math.floor(math.log(1024 / 256 / lngFraction) / math.log(2))
	zoom = min([latZoom, lngZoom, 21])
	return (mid_x, mid_y, zoom)
	#return data

def generate_html(data):
	span, increment = calc_span_increment(data)

	mm_ss = "return date.getHours() + ':' + date.getMinutes()"
	hh_mm = "var hrs = date.getHours(), mins = date.getMinutes(); return (hrs > 12 ? hrs - 12 : hrs) + ':' + (mins < 10 ? '0' + mins : mins) + ' ' + (hrs >= 12 ? 'pm' : 'am');"
	yyyy_mm_dd_hh_mm = "var hrs = date.getHours(), mins = date.getMinutes(), month = date.getMonth() + 1, day = date.getDate(); return date.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day) + ' ' + (hrs > 12 ? hrs - 12 : hrs) + ':' + (mins < 10 ? '0' + mins : mins) + ' ' + (hrs >= 12 ? 'pm' : 'am');"
	yyyy_mm_dd = "var month = date.getMonth() + 1, day = date.getDate(); return date.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day);"
	yyyy = "return date.getFullYear()"

	if span < hour:
		date_format_str = mm_ss
	elif span < day:
		date_format_str = hh_mm
	elif span < 180 * day:
		date_format_str = yyyy_mm_dd_hh_mm
	elif span < 15 * year:
		date_format_str = yyyy_mm_dd
	else:
		date_format_str = yyyy
	
	fast = round(3000 / (span / increment), 2) # three seconds
	medium = 2 * fast
	slow = 2 * medium
	
	#print 'divsor:', (span // increment), 'span:', span, 'increment', increment, 'fast:', fast
	#total_increments = span / increment
	#print 'increments:' + str(total_increments)

	x, y, zoom = calc_centroid_zoom(data)

	start_time = data['start_time']
	end_time = data['end_time']

	duration = pointSize = feather = "null"

	header = open('header.html', 'r')
	footer = open('footer.html', 'r')
	
	t =   "      var datasets = [{ name: '%s', url: '%s', duration: %s, feather: %s, pointSize: %s }];\n" % (data['base_name'], data['bin_url'], duration, pointSize, feather)
	t +=  "      var mapOptions = {\n"
	t +=  "        zoom: %s,\n" % zoom
	t +=  "        center: new google.maps.LatLng(%s, %s),\n" % (y, x)
	t +=  "        mapTypeControl: true\n"
	t +=  "      };\n"

	t +=  "      var timeSliderOptions = { \n"
	t +=  "        startTime: new Date(%s,%s,%s,%s,%s,%s).getTime(), \n" % (start_time.year, start_time.month - 1, start_time.day, start_time.hour, start_time.minute, start_time.second)
	t +=  "        endTime: new Date(%s,%s,%s,%s,%s,%s).getTime(), \n" % (end_time.year, end_time.month - 1, end_time.day, end_time.hour, end_time.minute, end_time.second)
	t +=  "        dwellAnimationTime: 2 * 1000, \n"
	t +=  "        increment: %s, \n" % (increment)
	t +=  "        formatCurrentTime: function(date) { %s },\n" % date_format_str
	t +=  "        animationRate: { fast: %s, medium: %s, slow: %s }\n" % (fast, medium, slow)
	t +=  "      };"
	t +=  "    </script>"

	html = header.read() + "\n" + t + "\n" + footer.read()
	with open('index.html', 'w') as f:
		f.write(html)

	return data

def build_zip(data):
	try:
		import zlib
		compression = zipfile.ZIP_DEFLATED
	except:
		compression = zipfile.ZIP_STORED

	modes = { zipfile.ZIP_DEFLATED: 'deflated',  zipfile.ZIP_STORED:   'stored',   }

	print 'creating archive'
	zf = zipfile.ZipFile('result.zip', mode='w')
	try:
		print 'adding files with compression mode', modes[compression]
		zf.write('index.html', compress_type=compression)
		zf.write(data['bin_url'], compress_type=compression)
	finally:
		print 'closing'
		zf.close()


def main(file):
	base_name = string.split(os.path.basename(file), '.')[0]
	
	data = {
		'file': file,
		'base_name': base_name,
		'start_time': datetime.max,
		'end_time': datetime.min,
		'item_count': 0,
		'min_x': float('inf'),
		'max_x': -float('inf'),
		'min_y': float('inf'),
		'max_y': -float('inf'),
		'interval': None,
		'span': None,
		'bin_url': None
	}

	# 1. Determine the file format of the uploaded file
	# -- for now, assume lat/lon/time
	# 2. Generate the Binary File
	data = generate_lat_lon_time_binary(data)
	data = generate_html(data)
	build_zip(data)

if __name__ == "__main__":
	if (len(sys.argv) != 2) or (sys.argv[1][-3:] != 'csv'):
		print 'Invalid arguments. Please provide valid path to csv file. e.g. "#> python csv-to-zip.py /Users/megge/data.csv"'
	main(sys.argv[1])