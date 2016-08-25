import sys
path = r'C:\Users\markegge\work\timelapse-toolchain\scripts'
if path not in sys.path:
	sys.path.insert(0, path)
from create_maps import app as application