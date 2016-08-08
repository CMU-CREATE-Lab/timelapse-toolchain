# CMU CREATE Lab
# Python 2.7

import os, array, csv, json, math, sys
from datetime import datetime
from dateutil.parser import parse
import zipfile

start_time, end_time, item_count = None, None, None

def LonLatToPixelXY(lonlat):
	(lon, lat) = lonlat
	x = (lon + 180.0) * 256.0 / 360.0
	y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
	return [x, y]

def YearMonthDayToEpoch(year, month, day):
  return (datetime(int(year), int(month), int(day)) - datetime(1970, 1, 1)).total_seconds()

def generate_binary(file, output_dir):
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
			#date = parseTime(row[date_col])
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
		x,y = LonLatToPixelXY([lon,lat])
		if start_time is None or start_time > date:
			start_time = date
		if end_time is None or end_time < date:
			end_time = date
		epochtime = (date - datetime(1970, 1, 1)).total_seconds()
		data += [x,y,epochtime]

        output_path = os.path.join(output_dir, 'data.bin')
        with open(output_path, 'wb') as output_file:
                array.array('f', data).tofile(output_file)


def generate_html(file, output_dir):
        current_path = os.path.realpath(__file__)
        current_dir = os.path.dirname(current_path)
	header = open(os.path.join(current_dir, 'header.txt'), 'r')
	footer = open(os.path.join(current_dir, 'footer.txt'), 'r')

	second = 1000
	minute = 60 * second
	hour = 60 * minute
	day = 24 * hour
	year = 365 * day

	span = (end_time - start_time).total_seconds() * 1000

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

	#test_spans = [minute, hour, day, 30*day, 180*day, year, 5*year, 10*year, 25*year, 100*year]

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

	fast = 3000 / (span / increment)
	medium = 2 * fast
	slow = 2 * medium

	print 'divsor:', (span // increment), 'span:', span, 'increment', increment, 'fast:', fast
	total_increments = span / increment
	print 'increments:' + str(total_increments)

	ts =  "      var timeSliderOptions = { \n"
	ts += "        startTime: new Date(%s,%s,%s,%s,%s,%s).getTime(), \n" % (start_time.year, start_time.month - 1, start_time.day, start_time.hour, start_time.minute, start_time.second)
	ts += "        endTime: new Date(%s,%s,%s,%s,%s,%s).getTime(), \n" % (end_time.year, end_time.month - 1, end_time.day, end_time.hour, end_time.minute, end_time.second)
	ts += "        dwellAnimationTime: 2 * 1000, \n"
	ts += "        increment: %s, \n" % (increment)
	ts += "        formatCurrentTime: function(date) { %s },\n" % date_format_str
	ts += "        animationRate: { fast: %s, medium: %s, slow: %s }\n" % (fast, medium, slow)
	ts += "      };"

	html = header.read() + "\n" + ts + "\n" + footer.read()
	with open(os.path.join(output_dir, 'index.html'), 'w') as f:
		f.write(html)


def build_zip(input_dir, output_dir):
	try:
		import zlib
		compression = zipfile.ZIP_DEFLATED
	except:
		compression = zipfile.ZIP_STORED

	modes = { zipfile.ZIP_DEFLATED: 'deflated',  zipfile.ZIP_STORED:   'stored',   }

	print 'creating archive'
	zf = zipfile.ZipFile(os.path.join(output_dir, 'result.zip'), mode='w')
	try:
		print 'adding files with compression mode', modes[compression]
		zf.write(os.path.join(input_dir, 'index.html'), compress_type=compression)
		zf.write(os.path.join(input_dir, 'data.bin'), compress_type=compression)
	finally:
		print 'closing'
		zf.close()


def main(file, output_dir=None):
        if output_dir is None:
                output_dir = '.'
	generate_binary(file, output_dir)
	generate_html(file, output_dir)
        # For now, input and output dir for zip file are the same
	build_zip(input_dir=output_dir, output_dir=output_dir)

if __name__ == "__main__":
	if (len(sys.argv) != 2) or (sys.argv[1][-3:] != 'csv'):
		print 'Invalid arguments. Please provide valid path to csv file. e.g. "#> python csv-to-zip.py /Users/megge/data.csv"'
	main(sys.argv[1])
