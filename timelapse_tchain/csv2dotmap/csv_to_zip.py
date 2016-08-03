# CMU CREATE Lab
# Python 2.7

import os, array, csv, json, math, random, urllib2, sys
from datetime import datetime
import zipfile

from django.conf import settings

start_time, end_time, item_count = None, None, None

OUT_DIR = os.path.join(getattr(settings, "BASE_DIR"))

def LonLatToPixelXY(lonlat):
	(lon, lat) = lonlat
	x = (lon + 180.0) * 256.0 / 360.0
	y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
	return [x, y]

def YearMonthDayToEpoch(year, month, day):
  return (datetime(int(year), int(month), int(day)) - datetime(1970, 1, 1)).total_seconds()

def parseTime(t):
	fmt = None
	t = str(t).lower()
	if len(t) == 10:
		if t[4] == '-': # YYYY-MM-DD
			fmt = '%Y-%m-%d'
		elif t[4] == '/': # YYYY/MM/DD
			fmt = '%Y/%m/%d' 
		elif t[2] == '/': # MM/DD/YYYY
			fmt = '%m/%d/%Y'
	elif len(t) == 4:
		fmt = '%Y'
	elif len(t) == 19: # YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS
		if t[10] == 't':
			fmt = '%Y-%m-%dT%H:%M:%S'
		else:
			fmt = '%Y-%m-%d %H:%M:%S'
	elif len(t) == 23: # YYYY-MM-DD HH:MM:SS.000 or YYYY-MM-DDTHH:MM:SS.000
		if t[10] == 't':
			fmt = '%Y-%m-%dT%H:%M:%S.%f'
		else:
			fmt = '%Y-%m-%d %H:%M:%S.%f'
	if fmt is not None:
		try:
			return datetime.strptime(t, fmt)
		except ValueError:
			print 'Error parsing "' + t + '" with format "' + fmt + '"'
			raise
	else:
		raise ValueError('Unable to parse ' + f + '. Unknown format')

def generate_binary(file):
	global start_time, end_time, item_count
	# to do: implement handling of CSVs without headers
	rows = []
	with open(file) as f:
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
	
	data = []

	for row in rows:
		try:
			date = parseTime(row[date_col])
		except ValueError:
			print 'error converting date for: ', row
			continue
		try:
			lon = float(row[lon_col])
			lat = float(row[lat_col])
		except ValueError:
			print 'error converting coordinate for: ', row
			continue
		x,y = LonLatToPixelXY([lon,lat])
		if start_time is None or start_time > date:
			start_time = date
		if end_time is None or end_time < date:
			end_time = date
		epochtime = (date - datetime(1970, 1, 1)).total_seconds()
		data += [x,y,epochtime]

	f.close()
	array.array('f', data).tofile(open('data.bin', 'wb'))

def generate_html(file):
	header = open(os.path.join(OUT_DIR, 'csv2dotmap', 'header.txt'), 'r')
	footer = open(os.path.join(OUT_DIR, 'csv2dotmap', 'footer.txt'), 'r')

	middle = "var timeSliderOptions = { "
	middle += "startTime: new Date(%s,%s,%s).getTime(), " % (start_time.year, start_time.month - 1, start_time.day)
	middle += "endTime: new Date(%s,%s,%s).getTime(), " % (end_time.year, end_time.month - 1, end_time.day)
	middle +=  """dwellAnimationTime: 2 * 1000, 
          increment: 120*24*60*60*1000,
          formatCurrentTime: function(date) { // Define time label
              var month = date.getMonth() + 1, day = date.getDate();
              return date.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day);
          },
          animationRate: {
            fast: 20,
            medium: 40,
            slow: 80
          }
        };"""
	html = header.read() + "\n" + middle + "\n" + footer.read()
	with open('index.html', 'w') as f:
		f.write(html)
		f.close


def build_zip():
	try:
	    import zlib
	    compression = zipfile.ZIP_DEFLATED
	except:
	    compression = zipfile.ZIP_STORED

	modes = { zipfile.ZIP_DEFLATED: 'deflated',  zipfile.ZIP_STORED:   'stored',   }

	print 'creating archive'
	zf = zipfile.ZipFile(os.path.join(OUT_DIR, 'static', 'result.zip'), mode='w')
	try:
	    print 'adding files with compression mode', modes[compression]
	    zf.write('index.html', compress_type=compression)
	    zf.write('data.bin', compress_type=compression)
	finally:
	    print 'closing'
	    zf.close()


def main(file):
	generate_binary(file)
	generate_html(file)
	build_zip()

if __name__ == "__main__":
	if (len(sys.argv) != 2) or (sys.argv[1][-3:] != 'csv'):
		print 'Invalid arguments. Please provide valid path to csv file. e.g. "#> python csv-to-zip.py /Users/megge/data.csv"'
	main(sys.argv[1])
