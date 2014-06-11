__author__ = 'vivek'

import os

UPreprocessor = 'Gromacs'
USimulator = 'Gromacs'
UAnalyzer = 'LSDMap'

UNAME = 'vivek91'
REMOTE_HOST = 'stampede.tacc.utexas.edu-devel'
WALLTIME = 10
PILOTSIZE = 16
DBURL = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'

srcroot = os.path.dirname(os.path.abspath(__file__))

RCONF  = ['file://%s/my-xsede.json' % srcroot, 'file://%s/my-futuregrid.json' % srcroot]

lsdmap_loc = ''