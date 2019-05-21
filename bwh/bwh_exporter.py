import random
import time
import urllib.request
import glob
import darknet_lib
import os

#init the weighted network for performance-reasons - only at startup
darknet_lib.performDetect(initOnly=True)

#Use Random Folder to detect images
DEBUG = False
# Safe detected file to location
SAFE_FILE = False

#bees    = Gauge('count_of_bees', 'Count of Bees')
#wasps   = Gauge('count_of_wasps', 'Count of Wasps')
#hornets = Gauge('count_of_hornets', 'Count of Hornets')
#
#REQUEST_TIME = Gauge('request_processing_seconds', 'Time spent processing request')

def process_request():
	"""Get an Image from webcam and count objects"""
	if DEBUG:
		current_dir = os.path.dirname(os.path.abspath(__file__))
		file_list = glob.glob(os.path.join(current_dir,'..','random', "*.jpg"))
		random.shuffle(file_list)
		filename = file_list[0]
		print(filename)
		detections = darknet_lib.performDetect(imagePath=filename)
		print(detections)
	else:
		(filename, headers) = urllib.request.urlretrieve("https://home.jru.me/bee-cam/api.cgi?cmd=Snap&channel=0&rs=sdilj23SDO3DDGHJsdfs&user=guest&password=my_guest&1555017246")

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
	return metrics
#	bees.set(len(bees_))
#	wasps.set(len(wasps_))
#	hornets.set(len(hornets_))
