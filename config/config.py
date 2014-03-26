#!/usr/bin/env python
import os
# ----------------------------------------------------------------------------
# MAIN DESCRIPTION

RESOURCE = {
        #Resource related inputs	--MANDATORY
        'remote_host' : 'stampede.tacc.utexas.edu',
        'remote_directory' : '/home1/02734/vivek91/output/',
        'username' : 'vivek91',
        'number_of_cores' : 2,
        'walltime' : 5
    }

TASK = {
        #Task related inputs		--MANDATORY

        #Paths/Directories involved
        'source_directory' : '/home/vivek/Research/saga-pilot/Gromacs/gromacs_input_alanine_dipeptide/',
        'output_directory' : "",

        #kernel/wrapper names
        'kernel_type' : 'python',       #/bin/bash or python
        'app_kernel' : 'gromacs_python_wrapper.py',

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,

    }

RCONF  = ["file://localhost/home/vivek/MDEnsemble/config/my-futuregrid.json",
          "file://localhost/home/vivek/MDEnsemble/config/my-xsede.json"]

DBURL = "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/"
