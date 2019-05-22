import random
import time
import urllib.request
import glob
import darknet_lib
import os
from prometheus_client import Gauge, MetricsHandler, start_http_server
import click


from functools import wraps
def bwh_decorator(f):
#	@wraps(f)
	def wrapper(*args, **kwds):
	 process_request()
	 return f(*args, **kwds)
	return wrapper

@click.group(help='')
def cli():
    pass

@click.command()
@click.option('-p', '--port', help='Port to use', required=True, type=int)
@click.option('-w', '--webcam', help='webcam or picture-source to collect images from', default='https://home.jru.me/bee-cam/api.cgi?cmd=Snap&channel=0&rs=sdilj23SDO3DDGHJsdfs&user=guest&password=my_guest&1555017246', required=True, type=str)
def start(port, webcam):
	#init the weighted network for performance-reasons - only at startup
	darknet_lib.performDetect(initOnly=True)
	_webcam = webcam
	#Decorate http-get function to call process-request everytime it is called.
	MetricsHandler.do_GET = bwh_decorator(MetricsHandler.do_GET)
	# Start up the server to expose the metrics.
	start_http_server(port)

	input("Press Enter to end...")

cli.add_command(start)

#Use Random Folder to detect images
_DEBUG = True

_webcam = 'http://'
# Safe detected file to location # actual not implemented
#SAFE_FILE = False

bees    = Gauge('count_of_bees', 'Count of Bees')
wasps   = Gauge('count_of_wasps', 'Count of Wasps')
hornets = Gauge('count_of_hornets', 'Count of Hornets')
#
REQUEST_TIME = Gauge('request_processing_seconds', 'Time spent processing request')


@REQUEST_TIME.time()
def process_request():
	"""Get an Image from webcam and count objects"""
	if _DEBUG:
		current_dir = os.path.dirname(os.path.abspath(__file__))
		file_list = glob.glob(os.path.join(current_dir,'..','random', "*.jpg"))
		random.shuffle(file_list)
		filename = file_list[0]
		print(filename)
	else:
		(filename, headers) = urllib.request.urlretrieve(webcam)

	detections = darknet_lib.performDetect(imagePath=filename)
	if _DEBUG: print(detections)

	bees_ = []
	wasps_ = []
	hornets_ = []
	result_objects = {
	    b'bee': bees_,
	    b'wasp': wasps_,
	    b'hornet': hornets_
	}
	for (object, propability, box ) in detections:
		(result_objects.get(object)).append((propability, box))

	metrics = {
	'bees'   : len(bees_),
	'wasps'  : len(wasps_),
	'hornets': len(hornets_)
	}
#	return metrics
	bees.set(len(bees_))
	wasps.set(len(wasps_))
	hornets.set(len(hornets_))

if __name__ == '__main__':
    cli()
