#!/usr/bin/env python


RESOURCE = {
        #Resource related inputs	--MANDATORY
        'remote_host' : 'sierra.futuregrid.org',
        'remote_directory' : '/N/u/vivek91/output/',
        'number_of_cores' : 2,
        'walltime' : 5
    }

TASK = {
        #Task related inputs		--MANDATORY

        #Paths/Directories involved
        'source_directory' : '/home/vivek/Research/saga-pilot/Gromacs/gromacs_input_PYP/',
        'output_directory' : "",

        #kernel/wrapper names
        'kernel_type' : '/bin/bash',       #/bin/bash or python
        'kernel' : 'MDRun.sh',

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,

    }

UNAME = 'vivek91'

srcroot = os.path.dirname(os.path.abspath(__file__))

RCONF  = ["file://%s/my-futuregrid.json"%srcroot,
          "file://%s/my-xsede.json"%srcroot]

DBURL = "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
