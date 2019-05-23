# Bee, Wasp, Hornet - Prometheus-Exporter

## Installation
Please run

'''
python setup.py
'''


## Usage

Actual there is no Daemon-Mode. One option may be to run it via "screen".


'''
Usage: bwh_exporter.py start [OPTIONS]

Options:
  -p, --port INTEGER  Port to use  [required]
  -w, --webcam TEXT   url to webcam-JPG or picture-source to collect images
                      from  [required]
'''

# example
'''
 python bwh/bwh_exporter.py start -p 8004 -w
'''
