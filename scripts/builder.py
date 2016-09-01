
import os, csv, math, array, re
from datetime import datetime
from dateutil.parser import parse
import zipfile
import jinja2
import settings

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

def generate_binary(filename, project_id):
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
	lat_col_name = lon_col_name = date_col_name = None

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
		fieldnames = reader.fieldnames
		rows = [row for row in reader]

	def find_opt_in_fields(option, fieldnames):
		for field in fieldnames:
			match = re.search(option, field)
			if match:
				return field
		return None
	def search_options(option_list):
		for option in option_list:
			col_name = find_opt_in_fields(option, fieldnames)
			if col_name:
				return col_name
		else:
			return None
	# errors.append('Invalid column specification. Missing column for ' + option_list[0])
	lat_col_name = search_options(lats)
	lon_col_name = search_options(lons)
	date_col_name = search_options(dates)
	errors = []
	if not lat_col_name:
		errors.append('Invalid column specification. Missing column for latitude')
	if not lon_col_name:
		errors.append('Invalid column specification. Missing column for longitude')
	if not date_col_name:
		errors.append('Invalid column specification. Missing column for date/time')
	if len(errors) > 0:
		raise ValueError('\n'.join(errors))
		
	items = []
	geom_count = 0
	lat_total = lon_total = 0
	for row in rows:
		try:
			date = parse(row[date_col_name], ignoretz=True)
		except ValueError:
			#print 'error converting date for: ', row
			continue
		try:
			lon = float(row[lon_col_name])
			lat = float(row[lat_col_name])
		except ValueError:
			#print 'error converting coordinate for: ', row
			continue
			
		if not lat or not lon or abs(lat) >= 90 or abs(lon) >= 180:
			# should probably raise a warning or some such
			continue
		
		lon_total += lon
		lat_total += lat
		geom_count += 1

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
		try:
			y = 128.0 - math.log(math.tan((lat + 90.0) * math.pi / 360.0)) * 128.0 / math.pi
		except ValueError as e:
			raise ValueError("Error calc y for val: " + str(lat))
		epochtime = (date - datetime(1970, 1, 1)).total_seconds() # // time in epoch time (seconds since 1970) in UTC timezone
		items += [x,y,epochtime]
	params['avg_x'] = lon_total / geom_count
	params['avg_y'] = lat_total / geom_count

	bin_filename = os.path.join(settings.PROJECTS_DIR, project_id, 'data.bin')
	with open(bin_filename, 'wb') as f:
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


def calc_zoom(data):
	#sets default zoom level for 800 x 600
	latFraction = (math.radians(data['max_y']) - math.radians(data['min_y'])) / math.pi
	lngDiff = data['max_x'] - data['min_x']
	if lngDiff < 0:
		lngDiff += 360
	lngFraction = lngDiff / 360
	latZoom = math.floor(math.log(768 / 256 / latFraction) / math.log(2))
	lngZoom = math.floor(math.log(1024 / 256 / lngFraction) / math.log(2))
	zoom = min([latZoom + 2, lngZoom + 2, 21])
	return zoom


def get_fmt_fn(span):
	mm_ss = r"return date.getHours() + ':' + date.getMinutes()"
	hh_mm = r"var hrs = date.getHours(), mins = date.getMinutes(); return (hrs > 12 ? hrs - 12 : hrs) + ':' + (mins < 10 ? '0' + mins : mins) + ' ' + (hrs >= 12 ? 'pm' : 'am');"
	yyyy_mm_dd_hh_mm = r"""
		var hrs = date.getHours(), mins = date.getMinutes(), month = date.getMonth() + 1, day = date.getDate(); 
		return date.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day) + ' ' + (hrs > 12 ? hrs - 12 : hrs) + ':' + (mins < 10 ? '0' + mins : mins) + ' ' + (hrs >= 12 ? 'pm' : 'am');
		"""
	yyyy_mm_dd = r"""
		var month = date.getMonth() + 1, day = date.getDate(); 
		return date.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day);
		"""
	yyyy = "return date.getFullYear();"

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

	zoom = calc_zoom(data)

	duration = pointSize = hardness = "null"
	params = {
		"title": data['title'],
		"project_id": data['project_id'],
		"email": data['email'],
		"description": None,
		"map": {
			"zoom": zoom,
			"center": [data['avg_y'], data['avg_x']]
		},
		"timeSlider": {
			"startTime": (data['start_time'] - datetime(1970, 1, 1)).total_seconds() * 1000 + increment,
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
		"blend": "additive",
		"datasets": [{
			"name": data['project_id'],
			"url": "data.bin" ,
			"rgba": [0.89, 0.1, 0.01, 1.0],
			"duration": span,
			"hardness": 0.5,
			"pointSize": 10.0,
			"enabled": True
		}]
	}
	return params

def write_html(params):
	template = JINJA_ENVIRONMENT.get_template('project.html')
	html = template.render(params)
	filename = os.path.join(settings.PROJECTS_DIR, params['project_id'], 'index.html')
	with open(filename, 'w') as f:
		try:
			f.write(html)
		except:
			print 'error writing', filename
			raise
	return True	


def build_zip(project_id):
	try:
		import zlib
		compression = zipfile.ZIP_DEFLATED
	except:
		compression = zipfile.ZIP_STORED

	modes = { zipfile.ZIP_DEFLATED: 'deflated',  zipfile.ZIP_STORED:   'stored',   }

	project_dir = filename = os.path.join(settings.PROJECTS_DIR, project_id)
	filename = os.path.join(project_dir, project_id + ".zip")
	if os.path.exists(filename):
		os.unlink(filename)

	project_files = []
	for root, dirs, files in os.walk(project_dir):
		for file in files:
			project_files.append(os.path.join(root, file))
	
	with zipfile.ZipFile(filename, mode='w') as zf:
		for file in project_files:
			#print 'adding', file, 'with compression mode', modes[compression]
			filename = str(file).split(project_id)[-1][1:] # extract out the relative path from abs path
			zf.write(file, arcname=filename, compress_type=compression)
	return True

if __name__ == "__main__":
	import sys
	if (len(sys.argv) != 2): # or (sys.argv[1][-3:] != 'csv'):
		print 'Invalid arguments. Please provide valid path to csv file. e.g. "#> python csv-to-zip.py /Users/megge/data.csv"'
	#build_zip(sys.argv[1])
