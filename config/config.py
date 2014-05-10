#!/usr/bin/env python
import os

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
        #Keep the kernel and the files accessed by the kernel/that need to be transferred in the source_directory
        'source_directory' : '/home/vivek/Research/saga-pilot/Gromacs/gromacs_input_PYP/',
        'output_directory' : "",

        #kernel/wrapper names
        'kernel_type' : '/bin/bash',       #/bin/bash or python
        'kernel' : 'MDRun.sh',      #this file should contain all the bash level commands/functions that are executed

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,

    }

UNAME = os.getenv('RADICAL_PILOT_USERNAME')

srcroot = os.path.dirname(os.path.abspath(__file__))

RCONF  = ["file://%s/my-futuregrid.json"%srcroot,
          "file://%s/my-xsede.json"%srcroot]

DBURL = os.getenv('RADICAL_PILOT_DBURL')
