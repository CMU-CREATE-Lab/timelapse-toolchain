
import os, csv, math, array
from datetime import datetime
from dateutil.parser import parse
import zipfile
import jinja2

# some useful constants	
second = 1000
minute = 60 * second
hour = 60 * minute
day = 24 * hour
year = 365 * day

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def generate_binary(filename, destination_filename):
	params = {
		'start_time': datetime.max,
		'end_time': datetime.min,
		'min_x': float('inf'),
		'max_x': -float('inf'),
		'min_y': float('inf'),
		'max_y': -float('inf'),
	}

	lats = ['latitude', 'lat', 'y']
	lons = ['longitude','lon', 'lng', 'long', 'x']
	dates = ['date', 'time', 'datetime', 'dates', 'times', 't', 'year', 'timestamp']

	rows = None
	reader = None
	with open(filename, 'rb') as file:
		sample = file.read(1024)
		file.seek(0)
		dialect = csv.Sniffer().sniff(sample)
		has_header = csv.Sniffer().has_header(sample)

		if has_header:
			reader = csv.DictReader(file)
			next(reader)
		else:
			reader = csv.DictReader(file, fieldnames=('lat', 'lon', 'time'))
		reader.fieldnames = [name.lower() for name in reader.fieldnames]
		col_names = reader.fieldnames
		rows = [row for row in reader]
	try:
		lat_col_name = next(iter(set(lats) & set(col_names)))
		lon_col_name = next(iter(set(lons) & set(col_names)))
		date_col_name = next(iter(set(dates) & set(col_names)))
	except StopIteration:
		display_error('Invalid column specification.')

	items = []
	for row in rows:
		try:
			date = parse(row[date_col_name], ignoretz=True)
		except ValueError:
			print 'error converting date for: ', row
			continue
		try:
			lon = float(row[lon_col_name])
			lat = float(row[lat_col_name])
		except ValueError:
			print 'error converting coordinate for: ', row
			continue
		
		if lon > params['max_x']:
			params['max_x'] = lon
		elif lon < params['min_x']:
			params['min_x'] = lon
		if lat > params['max_y']:
			params['max_y'] = lat
		elif lat < params['min_y']:
			params['min_y'] = lat

		if date < params['start_time']:
			params['start_time'] = date
		if date > params['end_time']:
			params['end_time'] = date

		x = (lon + 180.0) * 256.0 / 360.0
		y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
		epochtime = (date - datetime(1970, 1, 1)).total_seconds() # // time in epoch time (seconds since 1970) in UTC timezone
		items += [x,y,epochtime]

	with open(destination_filename, 'wb') as f:
		array.array('f', items).tofile(f)
	os.unlink(filename)
	return params

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

def get_fmt_fn(span):
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
	return date_format_str

def generate_params(data):
	span, increment = calc_span_increment(data)
	fmt_str = get_fmt_fn(span)
	
	fast = round(3000 / (span / increment), 2) # three seconds
	medium = 2 * fast
	slow = 2 * medium
	
	total_increments = span // increment

	x, y, zoom = calc_centroid_zoom(data)

	duration = pointSize = hardness = "null"
	params = {
	    "title": data['title'],
	    "project_id": data['project_id'],
	    "email": data['email'],
	    "description": None,
	    "map": {
	        "zoom": zoom,
	        "center": [y, x]
	    },
	    "timeSlider": {
	        "startTime": (data['start_time'] - datetime(1970, 1, 1)).total_seconds() * 1000,
	        "endTime": (data['end_time'] - datetime(1970, 1, 1)).total_seconds() * 1000,
	        "dwellAnimationTime": 2000,
	        "increment": increment,
		"timeFormat": fmt_str,
	        "animationRate": {
	            "fast": fast,
	            "medium": medium,
	            "slow": slow
	        }
	    },
	    "blend": "solid",
	    "datasets": [{
	        "name": data['project_id'],
	        "url": "data.bin" ,
	        "rgba": [0.89, 0.1, 0.11, 1.0],
	        "duration": span,
	        "hardness": 0.5,
	        "pointSize": 10.0,
	        "enabled": True
	    }]
	}
	return params

def write_html(params, destination_filename):
	template = JINJA_ENVIRONMENT.get_template('project.html')
	html = template.render(params)
	with open(destination_filename, 'w') as f:
		try:
			f.write(html)
		except:
			print 'error writing', filename
			raise
	return True	


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