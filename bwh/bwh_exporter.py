import random
import time
import urllib.request
import glob
import darknet_lib
import os
from prometheus_client import Gauge, MetricsHandler, start_http_server
import skimage
import numpy as np

#Use 'Random' Folder to detect images
_DEBUG = False

import argparse
# input arguments
# ----------------------------
parser = argparse.ArgumentParser(description='')
parser.add_argument('-p', '--port', type=int, required=True, help='Port to use')
parser.add_argument('-w', '--webcam', default='https://home.jru.me/bee-cam/api.cgi?cmd=Snap&channel=0&rs=sdilj23SDO3DDGHJsdfs&user=guest&password=my_guest&1555017246',required=True, type=str, help='webcam or picture-source to collect images from')
parser.add_argument('-o', '--output_img', default='output.jpg', type=str, help='Location and Filename of output.jpg')

args = parser.parse_args()
webcam = args.webcam
port = args.port
output = args.output_img
# ----------------------------


import logging
#-------------Logging facilities - to get more Output setLevel(logging.DEBUG) less for setLevel(logging.WARN)
# create logger
logger = logging.getLogger(os.path.basename(__file__))
#logger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
#ch.setLevel(logging.INFO)
ch.setLevel(logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.basename(__file__)+'.log')
fh.setLevel(logging.ERROR)

# create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
# -------------------------------

# decorator to adapt DO_GET Function of HTTP-Server and calculate bees, wasps and hornets only on request
from functools import wraps
def bwh_decorator(f):
#	@wraps(f)
	def wrapper(*args, **kwds):
	 process_request() # here works the magic
	 return f(*args, **kwds)
	return wrapper

# Safe detected file to location # actual not implemented
#SAFE_FILE = False

# Counted Objects - for more details please check prometheus docs
bees    = Gauge('count_of_bees', 'Count of Bees')
wasps   = Gauge('count_of_wasps', 'Count of Wasps')
hornets = Gauge('count_of_hornets', 'Count of Hornets')

REQUEST_TIME = Gauge('request_processing_seconds', 'Time spent processing request')


@REQUEST_TIME.time()
def process_request():
	"""Get an Image from webcam and count objects"""
	logger.debug("url: {}".format(webcam))
	if _DEBUG:
		current_dir = os.path.dirname(os.path.abspath(__file__))
		file_list = glob.glob(os.path.join(current_dir,'..','random', "*.jpg"))
		random.shuffle(file_list)
		filename = file_list[0]
		logger.debug("used file: {}".format(filename))
	else:
		(filename, headers) = urllib.request.urlretrieve(webcam)

	detections = darknet_lib.performDetect(imagePath=filename)
	logger.debug(detections)
	# TODO: input-argument to save optional and to save to given path
	skimage.io.imsave(output,darknet_lib.make_image(imagePath=filename,detections=detections),quality=90)

	bees_ = []
	wasps_ = []
	hornets_ = []
	# Objects are not string - byte-code string
	result_objects = {
	    b'bee': bees_,
	    b'wasp': wasps_,
	    b'hornet': hornets_
	}
	for (object, propability, box ) in detections:
		(result_objects.get(object)).append((propability, box))
	#eventually Histogramm to adapt propabilities in graf? - optional
	bees.set(len(bees_))
	wasps.set(len(wasps_))
	hornets.set(len(hornets_))

if __name__ == '__main__':
	#init the weighted network for performance-reasons - only at startup
	darknet_lib.performDetect(initOnly=True)
	logger.debug("Webcam-Url: {}".format(webcam))
	#Decorate http-get function to call process-request everytime it is called.
	MetricsHandler.do_GET = bwh_decorator(MetricsHandler.do_GET)
	# Start up the server to expose the metrics.
	start_http_server(port)

	input("Press 'Enter' to end application / Httpserver works in Background until then...")
